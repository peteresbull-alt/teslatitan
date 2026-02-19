from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

# from .constants import ACCOUNTS
from .serializers import SupportSerializer

from django.contrib.auth import update_session_auth_hash
import json

from django.core.mail import send_mail

from rest_framework.permissions import AllowAny

from django.utils.crypto import get_random_string

# from .helpers import check_email, is_valid_password

from rest_framework.views import APIView

from django.contrib.auth import authenticate, login

from django.shortcuts import render
from app.models import (
    KYC,
    Transaction,
    CustomUser,
    Notification,
    AdminWallet,
    Support,
    CustomerPaymentInformation,
    Investment,
)
# 

from django.contrib.auth import get_user_model

from django.db.models import Sum, Count
from django.utils import timezone
from collections import defaultdict
import calendar
from django.db.models.functions import ExtractMonth

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from app.models import Support
from app.models import CustomUser
from django.contrib import messages

from django.conf import settings

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart



logger = logging.getLogger(__name__)


User = CustomUser



@method_decorator(csrf_exempt, name='dispatch')
class ContactFormView(APIView):
    """
    API endpoint to send contact form emails using smtplib
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        # Extract form data
        full_name = request.data.get('full_name', '').strip()
        email = request.data.get('email', '').strip()
        phone = request.data.get('phone', '').strip()
        subject = request.data.get('subject', '').strip()
        message = request.data.get('message', '').strip()

        print(request.data)
        
        # Validate required fields
        if not all([full_name, email, subject, message]):
            return Response(
                {'error': 'Please fill in all required fields'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Basic email validation
        if '@' not in email or '.' not in email:
            return Response(
                {'error': 'Please provide a valid email address'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Verify email settings exist
            if not all([
                settings.EMAIL_HOST,
                settings.EMAIL_PORT,
                settings.EMAIL_HOST_USER,
                settings.EMAIL_HOST_PASSWORD
            ]):
                logger.error('Email configuration is incomplete in settings.py')
                return Response(
                    {'error': 'Email service is not configured. Please contact support.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Send email using smtplib
            self.send_html_email(
                to_email=settings.OWNER_ADMIN_EMAIL,  # Send to your support email
                subject=f'Contact Form: {subject}',
                full_name=full_name,
                email=email,
                phone=phone,
                user_subject=subject,
                message=message
            )
            
            return Response(
                {'success': 'Your message has been sent successfully! We\'ll get back to you within 24 hours.'},
                status=status.HTTP_200_OK
            )
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f'SMTP Authentication failed: {str(e)}')
            return Response(
                {'error': 'Email authentication failed. Please contact support.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except smtplib.SMTPException as e:
            logger.error(f'SMTP error occurred: {str(e)}')
            return Response(
                {'error': 'Failed to send email. Please try again later.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f'Unexpected error sending email: {str(e)}')
            return Response(
                {'error': 'An unexpected error occurred. Please try again later.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def send_html_email(self, to_email, subject, full_name, email, phone, user_subject, message):
        """
        Send HTML email using smtplib with SSL
        """
        # Create message container
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = settings.EMAIL_HOST_USER
        msg['To'] = to_email
        
        # Create HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f4f4f4;
                }}
                .container {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 15px;
                    padding: 30px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                }}
                .header {{
                    text-align: center;
                    color: white;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                }}
                .content {{
                    background: white;
                    border-radius: 10px;
                    padding: 25px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }}
                .field {{
                    margin-bottom: 20px;
                    padding-bottom: 15px;
                    border-bottom: 1px solid #e0e0e0;
                }}
                .field:last-child {{
                    border-bottom: none;
                }}
                .label {{
                    font-weight: bold;
                    color: #667eea;
                    font-size: 12px;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    margin-bottom: 5px;
                }}
                .value {{
                    color: #333;
                    font-size: 16px;
                    word-wrap: break-word;
                }}
                .message-box {{
                    background: #f9f9f9;
                    padding: 15px;
                    border-radius: 8px;
                    border-left: 4px solid #667eea;
                    margin-top: 10px;
                }}
                .footer {{
                    text-align: center;
                    color: white;
                    margin-top: 20px;
                    font-size: 12px;
                    opacity: 0.9;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📧 New Contact Form Submission</h1>
                </div>
                <div class="content">
                    <div class="field">
                        <div class="label">Full Name</div>
                        <div class="value">{full_name}</div>
                    </div>
                    <div class="field">
                        <div class="label">Email Address</div>
                        <div class="value"><a href="mailto:{email}" style="color: #667eea; text-decoration: none;">{email}</a></div>
                    </div>
                    {f'<div class="field"><div class="label">Phone Number</div><div class="value">{phone}</div></div>' if phone else ''}
                    <div class="field">
                        <div class="label">Subject</div>
                        <div class="value">{user_subject}</div>
                    </div>
                    <div class="field">
                        <div class="label">Message</div>
                        <div class="message-box">{message.replace(chr(10), '<br>')}</div>
                    </div>
                </div>
                <div class="footer">
                    <p>This email was sent from the TitanStocks contact form</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version as fallback
        text_content = f"""
        New Contact Form Submission
        
        Full Name: {full_name}
        Email: {email}
        Phone: {phone if phone else 'Not provided'}
        Subject: {user_subject}
        
        Message:
        {message}
        
        ---
        This email was sent from the TitanStocks contact form
        """
        
        # Attach both versions
        part1 = MIMEText(text_content, 'plain')
        part2 = MIMEText(html_content, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email via SMTP_SSL (port 465)
        try:
            with smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=10) as server:
                # server.set_debuglevel(1)  # Uncomment for debugging
                server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                server.send_message(msg)
                logger.info(f'Email sent successfully to {to_email}')
        except Exception as e:
            logger.error(f'Failed to send email: {str(e)}')
            raise




@api_view(['POST'])
def register_api_view(request):
    if request.method == 'POST':

        print(request.data)

        required_fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'annual_income',
            'profile_image',
            'password', 'password_confirmation'
        ]

        first_name=request.data.get('first_name')
        last_name=request.data.get('last_name')
        email=request.data.get('email')       
        phone_number=request.data.get('phone_number')      
        annual_income=request.data.get('annual_income')
        program_type=request.data.get('program_type')

        country=request.data.get('country')
        state=request.data.get('state')
        postal_code=request.data.get('postal_code')
        date_of_birth=request.data.get('dob')
        city=request.data.get('city')
        address=request.data.get('address')
        citizenship_status=request.data.get('citizenship_status')
        profile_image=request.FILES.get('profile_image')
        password=request.data.get('password')
        preferred_currency = request.data.get('preferred_currency')
        
        password_confirmation=request.data.get('password_confirmation')

        existing_user = User.objects.filter(email=email).first()

        if existing_user:
            return Response({"error": "User with email already exists."}, status=status.HTTP_400_BAD_REQUEST)
        

        # Check for missing fields
        missing_fields = [field for field in required_fields if field not in request.data]
        if missing_fields:
            return Response(
                {"error": f"Missing fields: {', '.join(missing_fields)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if password != password_confirmation:
            return Response({"error": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number,
                annual_income=annual_income,
                city=city,
                postal_code=postal_code,
                date_of_birth=date_of_birth,
                address=address,
                country=country,
                state=state,
                profile_image=profile_image,
                citizenship_status=citizenship_status,
                program_type=program_type,
                user_password_in_text=password,
                preferred_currency=preferred_currency,
            )
            user.preferred_currency = preferred_currency
            user.set_password(password)
            user.save()

            


            # send_beautiful_html_email_create_user(
            #     bank_id=user.bank_id,
            #     account_details=f"Account Type: {user.preferred_account_type}, Balance: $0",
            #     to_email=user.email,
            # )

            # send_admin_mail(
            #     subject="New user Alert",
            #     message="Hi, a new user just registered and is ready for activation",
            # )

            return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
@api_view(['POST'])
def change_password_api_view(request):
    data = request.data
    new_password = data.get("new_password")
    old_password = data.get("old_password")
    confirm_password = data.get("confirm_password")

    user = request.user

    if new_password != confirm_password:
        print("New passwords do not match.")
        return Response({'error': 'New passwords do not match.', 'success': False}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if user old_password is correct
    if not user.check_password(old_password):
        return Response({'error': 'Current password is incorrect.', 'success': False}, status=status.HTTP_400_BAD_REQUEST)
    
    request.user.set_password(new_password)
    request.user.save()
    # Prevents logging out after password change
    update_session_auth_hash(request, request.user)


    return Response({'message': 'Password updated successfully.', 'success': True}, status=status.HTTP_201_CREATED)
















@api_view(['POST'])
def login_with_email_api(request):
    email = request.data.get('email')
    password = request.data.get('password')

    

    print(f"Details {email} {password}")

    try:
        user = CustomUser.objects.get(email=email)
        user = authenticate(request, email=user.email, password=password)
        if user is not None:
            login(request, user)

            # send_admin_mail(
            #     subject="Login Alert",
            #     message=f"User with email: {request.user.email} just logged into the app."
            # )
            # send_ordinary_user_mail(
            #     to_email=request.user.email,
            #     subject="Login Alert",
            #     message="We noticed a login attempt you made. Please know we take security very seriously at \
            #         Optimum Bank and we are dedicated to giving you the best banking experience."
            # )

            # Change the redirect url here if you change the dashboard
            return Response({'message': 'Login successful', 'redirect_url': '/dashboard'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials. Ensure your email and password are correct.'}, status=status.HTTP_401_UNAUTHORIZED)
    except CustomUser.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)






@api_view(['POST'])
def update_profile_api_view(request):
    if request.method == "POST":
        data = request.data
        files = request.FILES

        user = request.user

        first_name = data.get("first_name")
        last_name = data.get("last_name")
        state = data.get("state")
        city = data.get("city")
        country = data.get("country")
        address = data.get("address")
        profile_image = files.get("profile_image")

        user.first_name = first_name
        user.last_name = last_name
        user.state = state
        user.city = city
        user.country = country
        user.address = address

        if profile_image:
            user.profile_image = profile_image

        user.save()

        return Response({"message": "Profile updated successfully.", 'success': True}, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Method is not allowed.", 'success': False}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def support_api(request):
    serializer = SupportSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        # send_admin_mail(
        #         subject="Login Alert",
        #         message=f"User with email {request.user.email} just logged into the app."
        # )
        # send_ordinary_user_mail(
        #     to_email=request.user.email,
        #         subject="Login Alert",
        #         message="We noticed a login attempt you made. Please know we take security very seriously at \
        #             Optimum Bank and we are dedicated to giving you the best banking experience."
        # )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clear_user_notification(request):
    # Bulk update all unread notifications for the user
    updated_count = Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    
    return Response({
        "message": f"{updated_count} notifications have been marked as read!",
        "count": updated_count
    })


@api_view(['POST'])
def KYCAPIView(request):
    data = request.data
    files = request.FILES
    
    print(data)

    marital_choice = data.get('marital_choice')
    number_of_dependents = data.get('number_of_dependents')
    employment_type = data.get('employment_type')
    employment_status = data.get('employment_status')
    
    citizenship_status = data.get('citizenship_status')
    ssn = data.get('ssn')
    tax_identity_number = data.get('tax_identity_number')
    government_id_type = data.get('government_id_type')
    government_id_number = data.get('government_id_number')

    proof_of_employment = files.get('proof_of_employment')
    proof_of_income = files.get('proof_of_income')
    front_id_image = files.get('front_id_image')
    back_id_image = files.get('back_id_image')
    image_holding_id = files.get('image_holding_id')

    try:
        kyc_details = KYC(
            user=request.user,
            marital_choice=marital_choice,
            number_of_dependents=number_of_dependents,
            employment_status=employment_status,
            employment_type=employment_type,
            citizenship_status=citizenship_status,
            ssn=ssn,
            tax_identity_number=tax_identity_number,
            government_id_type=government_id_type,
            government_id_number=government_id_number,
            proof_of_employment=proof_of_employment,
            proof_of_income=proof_of_income,
            front_id_image=front_id_image,
            back_id_image=back_id_image,
            image_holding_id=image_holding_id,
        )

        request.user.has_submitted_kyc = True

        request.user.save()
        kyc_details.save()

        return Response({
            "message": "KYC is being evaluated. We will contact you in due time once your documents have been reviewed.", 
            "success": True
        }, status=status.HTTP_200_OK)

    except Exception as e:
        print(e)
        return Response({"message": "We encountered a problem while updating your KYC. Please try again later."}, status=status.HTTP_400_BAD_REQUEST)





@api_view(['POST'])
def update_payment_information_api(request):
    """Create a new saved payment method for the authenticated user."""
    user = request.user
    withdrawal_type = request.data.get("withdrawal_type")
    label = (request.data.get("label") or "").strip() or None

    if withdrawal_type not in ("BANK_WIRE", "CRYPTO"):
        return Response({"message": "Invalid payment method type.", "success": False}, status=status.HTTP_400_BAD_REQUEST)

    kwargs = dict(user=user, withdrawal_type=withdrawal_type, label=label)

    if withdrawal_type == "BANK_WIRE":
        bank_account_number = (request.data.get("bank_account_number") or "").strip()
        if not request.data.get("bank_name") or not request.data.get("bank_account_name") or not bank_account_number:
            return Response({"message": "Bank name, account holder name and account number are required.", "success": False}, status=status.HTTP_400_BAD_REQUEST)
        if CustomerPaymentInformation.objects.filter(user=user, withdrawal_type="BANK_WIRE", bank_account_number=bank_account_number).exists():
            return Response({"message": "You already have a bank account with that account number saved.", "success": False}, status=status.HTTP_400_BAD_REQUEST)
        kwargs.update(
            bank_name=request.data.get("bank_name"),
            bank_account_name=request.data.get("bank_account_name"),
            bank_account_number=bank_account_number,
            routing_number=request.data.get("routing_number"),
            swift_code=request.data.get("swift_code"),
            bank_address=request.data.get("bank_address"),
        )
    else:
        crypto_address = (request.data.get("crypto_address") or "").strip()
        crypto_type = (request.data.get("crypto_type") or "").strip()
        if not crypto_address or not crypto_type:
            return Response({"message": "Crypto type and wallet address are required.", "success": False}, status=status.HTTP_400_BAD_REQUEST)
        if CustomerPaymentInformation.objects.filter(user=user, withdrawal_type="CRYPTO", crypto_address=crypto_address).exists():
            return Response({"message": "You already have that wallet address saved.", "success": False}, status=status.HTTP_400_BAD_REQUEST)
        kwargs.update(crypto_address=crypto_address, crypto_type=crypto_type)

    try:
        CustomerPaymentInformation.objects.create(**kwargs)
        return Response({"message": "Payment method saved successfully.", "success": True}, status=status.HTTP_201_CREATED)
    except Exception:
        return Response({"message": "Unable to save payment method. Please try again later.", "success": False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
def delete_payment_method_api(request, pk):
    """Delete one of the authenticated user's saved payment methods."""
    try:
        method = CustomerPaymentInformation.objects.get(pk=pk, user=request.user)
        method.delete()
        return Response({"message": "Payment method removed.", "success": True}, status=status.HTTP_200_OK)
    except CustomerPaymentInformation.DoesNotExist:
        return Response({"message": "Payment method not found.", "success": False}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
def edit_payment_method_api(request, pk):
    """Edit one of the authenticated user's saved payment methods."""
    try:
        method = CustomerPaymentInformation.objects.get(pk=pk, user=request.user)
    except CustomerPaymentInformation.DoesNotExist:
        return Response({"message": "Payment method not found.", "success": False}, status=status.HTTP_404_NOT_FOUND)

    method.label = (request.data.get("label") or "").strip() or None

    if method.withdrawal_type == "BANK_WIRE":
        method.bank_name = request.data.get("bank_name", method.bank_name)
        method.bank_account_name = request.data.get("bank_account_name", method.bank_account_name)
        method.bank_account_number = request.data.get("bank_account_number", method.bank_account_number)
        method.routing_number = request.data.get("routing_number", method.routing_number)
        method.swift_code = request.data.get("swift_code", method.swift_code)
        method.bank_address = request.data.get("bank_address", method.bank_address)
    else:
        method.crypto_address = request.data.get("crypto_address", method.crypto_address)
        method.crypto_type = request.data.get("crypto_type", method.crypto_type)

    method.save()
    return Response({"message": "Payment method updated successfully.", "success": True}, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_wallet_address(request, wallet_type):
    try:
        wallet = AdminWallet.objects.get(wallet_type=wallet_type)
        return Response({"wallet_address": wallet.wallet_address}, status=200)
    except AdminWallet.DoesNotExist:
        return Response({"error": "Wallet type not found"}, status=404)

@api_view(['POST'])
def funding_account_request_api(request):
    user = request.user

    if request.method == 'POST':
        amount = request.data.get("amount")
        transaction_type = request.data.get("transaction_type")
        confirmation_receipt = request.FILES.get("confirmation_receipt")
        payment_method = request.data.get("payment_method")
        wallet = request.data.get("wallet")

        print(request.data)

        Transaction.objects.create(
            user=user,
            amount=amount,
            transaction_type="FUNDING",
            confirmation_receipt=confirmation_receipt,
            payment_method=payment_method,
            wallet=wallet
        )
        return Response({"message": "Your payment receipt has been uploaded and is currently being reviewed. Your account will be funded after confirmation! ", "success": True}, status=status.HTTP_200_OK) 

    else:
        return Response({
            "message": "Invalid request method. Only POST is allowed.", 
            "success": True}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    
    
@api_view(['POST'])
def withdrawal_request_api(request):

    user = request.user

    

    if request.method == 'POST':
        user_roi = user.roi
        user_capital = user.capital
        user_bonus = user.bonus

        amount = int(request.data.get("amount"))
        payment_method = request.data.get("payment_method")
        withdraw_source = request.data.get("withdraw_source")
        withdrawal_type = request.data.get("withdrawal_type")  # BANK_WIRE or CRYPTO

        if withdraw_source == "roi":
            if amount > user_roi:
                return Response({"message": "Insufficient ROI to withdraw", "success": False}, status=status.HTTP_400_BAD_REQUEST)
        elif withdraw_source == "capital":
            if amount > user_capital:
                return Response({"message": "Insufficient Capital to withdraw", "success": False}, status=status.HTTP_400_BAD_REQUEST)
        elif withdraw_source == "bonus":
            if amount > user_bonus:
                return Response({"message": "Insufficient Bonus to withdraw", "success": False}, status=status.HTTP_400_BAD_REQUEST)

        transaction_kwargs = dict(
            user=user,
            amount=amount,
            payment_method=payment_method,
            withdraw_source=withdraw_source,
            transaction_type="WITHDRAWAL",
            withdrawal_type=withdrawal_type,
        )

        if withdrawal_type == "BANK_WIRE":
            transaction_kwargs["bank_name"] = request.data.get("bank_name")
            transaction_kwargs["bank_account_name"] = request.data.get("bank_account_name")
            transaction_kwargs["bank_account_number"] = request.data.get("bank_account_number")
            transaction_kwargs["routing_number"] = request.data.get("routing_number")
            transaction_kwargs["swift_code"] = request.data.get("swift_code")
            transaction_kwargs["bank_address"] = request.data.get("bank_address")
        elif withdrawal_type == "CRYPTO":
            transaction_kwargs["crypto_address"] = request.data.get("crypto_address")
            transaction_kwargs["crypto_type"] = request.data.get("crypto_type")

        Transaction.objects.create(**transaction_kwargs)

    return Response({
            "message": "Your withdrawal request has been submitted and is pending review.",
            "success": True}, status=status.HTTP_200_OK)



    
@api_view(['POST'])
def investment_create_request_api(request):
    user = request.user
    print(request.data)
    amount = request.data.get("amount")
    investment_type = request.data.get("investment")

    

    try:
        int_amount = int(amount)
        user_capital = int(user.capital)
        if user_capital < int_amount:
            return Response({"message": "You do not have enough capital to invest. Your capital must be greater than the investment amount. Please fund your account. ", "success": False}, status.HTTP_400_BAD_REQUEST)
        
        user.investment += int_amount
        user.capital -= int_amount
        user.save()
    except ValueError as e:
        print(e)
        return Response({"message": "Enter a valid number for amount ", "success": False}, status.HTTP_400_BAD_REQUEST)

    Investment.objects.create(
        user=user,
        amount=amount,
        investment_type=investment_type,
    )
    return Response({"message": "Investment was seccussful. ", "success": True}, status.HTTP_200_OK)



















