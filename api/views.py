from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status

# from .constants import ACCOUNTS
from .serializers import SupportSerializer

from django.contrib.auth import update_session_auth_hash
import json

# from .email import (
#     send_beautiful_html_email_create_account, 
#     send_admin_mail, 
#     send_ordinary_user_mail,
#     send_mail_from_admin_to_user,
#     send_mail_for_payment_options,
#     send_contact_mail,
# )




from django.core.mail import send_mail
from django.utils.crypto import get_random_string

# from .helpers import check_email, is_valid_password

from rest_framework.views import APIView

from django.contrib.auth import authenticate, login

from django.shortcuts import render
from app.models import (
    KYC, 
    Payment, 
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

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from app.models import Support
# from .serializers import SupportSerializer, AccountActivationSerializer
from app.models import CustomUser
from django.contrib import messages

from django.conf import settings


# from .email import send_beautiful_html_email_create_user


User = CustomUser




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

    user = request.user
    
    payment_type = request.data.get("payment_type")
    address = request.data.get("address")

    try:
        customer_payment_info = CustomerPaymentInformation.objects.filter(user=user).first()
        # Check if user already has a CustomerPaymentInformation instance
        if customer_payment_info:
            customer_payment_info.payment_type = payment_type
            customer_payment_info.payment_address = address
            customer_payment_info.save()
            return Response({"message": "Payment Information Updated Successfully. ", "success": True}, status=status.HTTP_200_OK)
        else:
            CustomerPaymentInformation.objects.create(
                user=user,
                payment_type=payment_type,
                payment_address=address
            )
            return Response({"message": "Payment Information Created Successfully. ", "success": True}, status=status.HTTP_200_OK)
    except:
        return Response({"error": "Unable to update payment information. Please try again later. ", "success": False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

        Payment.objects.create(
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

        if withdraw_source == "roi":
            if amount > user_roi:
                return Response({"message": "Insufficient ROI to withdraw", "success": False}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # user.roi -= amount
                # user.save()
                pass
        elif withdraw_source == "capital":
            if amount > user_capital:
                return Response({"message": "Insufficient Capital to withdraw", "success": False}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # user.capital -= amount
                # user.save()
                pass
        elif withdraw_source == "bonus":
            if amount > user_bonus:
                return Response({"message": "Insufficient Bonus to withdraw", "success": False}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # user.bonus -= amount
                # user.save()
                pass
    
        

        print(request.data)
        print(f"User ROI: {user_roi}; User Capital: {user_capital}; User Bonus: {user_bonus}")

        Payment.objects.create(
            user=user,
            amount=amount,
            payment_method=payment_method,
            withdraw_source=withdraw_source,
            transaction_type="WITHDRAWAL",
        )


    return Response({
            "message": "Sorry, you have a pending transaction. ", 
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



















