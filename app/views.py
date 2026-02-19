from django.shortcuts import render
import json
from django.views.decorators.http import require_http_methods
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from functools import reduce
from django.db.models import Sum
from django.utils import timezone
from collections import defaultdict
import calendar
from django.db.models.functions import ExtractMonth
from django.http import JsonResponse

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import get_user_model
from django.http import Http404

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Plans

from .models import (
    Support,
    Notification,
    AdminWallet,
    Transaction,
    Investment,

)

User = get_user_model()

from .constants import (
    CITIZENSHIP_STATUSES,
    MARITAL_CHOICES,
    PREFERRED_CURRENCY,
    PROGRAM_TYPES,
    ACCOUNT_TYPES,
    EMPLOYMENT_STATUS,
    EMPLOYMENT_TYPE,
    PREFERRED_ID_TYPE,
    PAYMENT_TYPES,
    PAYMENT_METHODS,
    INVESTMENT_TYPES,
)


# Create your views here.


# -------------------------------- WEBSITE PAGES-------------------------------------
def home_page(request):
    return render(request, "website/index.html", {} )

def about_page(request):
    return render(request, "website/about.html", {} )

def crypto_page(request):
    return render(request, "website/crypto.html", {} )

def donate_page(request):
    admin_wallets = AdminWallet.objects.all()
    return render(request, "website/donate.html", {"admin_wallets": admin_wallets} )

def faqs_page(request):
    return render(request, "website/faqs.html", {} )

def contact(request):
    return render(request, "website/support.html", {} )




# -------------------------------- AUTH PAGES----------------------------------------
def login(request):
    if request.user.is_authenticated:
        return redirect("dashboard_home")
    return render(request, "dashboard/auth/login.html", {} )


@login_required
def LogoutView(request):
    logout(request)
    messages.success(request, 'Successfully logged out.')
    return redirect('login')

def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard_home")
    

    return render(request, "dashboard/auth/register.html", {
        "citizenship_statuses": CITIZENSHIP_STATUSES,
        "marital_choices": MARITAL_CHOICES,
        "program_types": PROGRAM_TYPES,
        "currencies": PREFERRED_CURRENCY,

    })

# View to handle password reset request
def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        reset_email_url = request.POST.get('password_url')
        user = User.objects.filter(email=email).first()
        
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = request.build_absolute_uri(f'/password-reset/{uid}/{token}/')
            
            # send_password_reset_email(to_email=user.email, reset_link=reset_url)
            return JsonResponse({'success': 'Password reset link was sent to your email'})
        else:
            return JsonResponse({'error': 'Email address not found'}, status=404)
    return render(request, 'dashboard/auth/password_reset_form.html')

# View to handle password reset form submission
def password_reset_confirm(request, uidb64, token):
    if request.method == 'POST':
        new_password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password == confirm_password:
            try:
                uid = force_str(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=uid)
                if default_token_generator.check_token(user, token):
                    user.set_password(new_password)
                    user.save()
                    
                    return JsonResponse({'success': 'Password reset successfully'})
                else:
                    return JsonResponse({'error': 'Invalid token'}, status=400)
            except Exception as e:
                return JsonResponse({'error': 'Invalid request'}, status=400)
        else:
            return JsonResponse({'error': 'Passwords do not match'}, status=400)

    return render(request, 'dashboard/auth/password_reset_confirm.html')




def password_reset_complete(request):
    return render(request, 'dashboard/auth/password_reset_complete.html')


# ------------------------------------------------------------------------------------



# -------------------------------- DASHBOARD PAGES-------------------------------------
@login_required
def dashboard_home(request):
    notifications = Notification.objects.filter(user=request.user).filter(is_read=False).order_by("-id")[:5]
    return render(request, "dashboard/major/index.html", {
        "notifications": notifications,
         "notification_count": notifications.count(),
    })
@login_required
def monitor_investment(request):
    notifications = Notification.objects.filter(user=request.user).filter(is_read=False).order_by("-id")[:5]
    return render(request, "dashboard/major/monitor_investment.html", {
        "notifications": notifications,
         "notification_count": notifications.count(),
    })

@login_required
def chart_analysis(request):
    notifications = Notification.objects.filter(user=request.user).filter(is_read=False).order_by("-id")[:5]
    return render(request, "dashboard/major/chart_analysis.html", {
        "notifications": notifications,
         "notification_count": notifications.count(),
    } )

@login_required
def fund_wallet(request):
    notifications = Notification.objects.filter(user=request.user).filter(is_read=False).order_by("-id")[:5]
    admin_wallets = AdminWallet.objects.all()
    
    return render(request, "dashboard/major/fund_wallet.html", {
        "notifications": notifications,
        "notification_count": notifications.count(),
        "currencies": PREFERRED_CURRENCY,
        "admin_wallets": admin_wallets,
    } )


@login_required
def withdraw_fund_wallet(request):
    notifications = Notification.objects.filter(user=request.user).filter(is_read=False).order_by("-id")[:5]

    return render(request, "dashboard/major/withdraw.html", {
        "notifications": notifications,
         "notification_count": notifications.count(),
        "currencies": PREFERRED_CURRENCY,
        "payment_methods": PAYMENT_METHODS,
    })

@login_required
def transactions(request):
    notifications = Notification.objects.filter(user=request.user).filter(is_read=False).order_by("-id")[:5]
    
    deposits = Transaction.objects.filter(user=request.user).filter(transaction_type="FUNDING").order_by("-id")
    withdrawals = Transaction.objects.filter(user=request.user).filter(transaction_type="WITHDRAWAL").order_by("-id")
    investments = Investment.objects.filter(user=request.user).order_by("-id")
    return render(request, "dashboard/major/transactions.html", {
        "notifications": notifications,
         "notification_count": notifications.count(),
         "deposits": deposits,
         "withdrawals": withdrawals,
         "investments": investments,
    })


@login_required
def investment_create(request):
    notifications = Notification.objects.filter(user=request.user).filter(is_read=False).order_by("-id")[:5]
    
    
    return render(request, "dashboard/major/investment_create.html", {
        "notifications": notifications,
         "notification_count": notifications.count(),
         "investment_options": INVESTMENT_TYPES,
    })


@login_required
def profile_details(request):
    notifications = Notification.objects.filter(user=request.user).filter(is_read=False).order_by("-id")[:5]
    
    return render(request, "dashboard/major/profile.html", {
        "notifications": notifications,  
        "notification_count": notifications.count(),
    })


@login_required
def profile_settings(request):
    notifications = Notification.objects.filter(user=request.user).filter(is_read=False).order_by("-id")[:5]
    return render(request, "dashboard/major/profile_settings.html", {
        "notifications": notifications,  
        "notification_count": notifications.count(),
    })



@login_required
def support_page(request):

    notifications = Notification.objects.filter(user=request.user).filter(is_read=False).order_by("-id")[:5]

    supports = Support.objects.filter(user=request.user).order_by("-id")[:5]

    return render(request, "dashboard/major/support.html", {
        "supports": supports,"notifications": notifications, 
        "notification_count": notifications.count(),
    })
    


@login_required
def notification_page(request):
    notifications = Notification.objects.filter(user=request.user).filter(is_read=False).order_by("-id")[:5]
    all_notifications = Notification.objects.filter(user=request.user).order_by("is_read", "-id")[:5]

    return render(request, "dashboard/major/notifications.html", {
        "notifications": notifications, 
        "notification_count": notifications.count(), 
        "all_notifications": all_notifications
    })

@login_required
def update_kyc(request):
    if request.user.has_verified_kyc:
        return redirect("dashboard_home")
    notifications = Notification.objects.filter(user=request.user).filter(is_read=False).order_by("-id")[:5]
    return render(request, "dashboard/major/kyc_page.html", {
            "employment_statuses": EMPLOYMENT_STATUS,
            "account_types": ACCOUNT_TYPES,
            "all_id_types": PREFERRED_ID_TYPE,
            "citizenship_statuses": CITIZENSHIP_STATUSES,
            "employment_types": EMPLOYMENT_TYPE,
            "marital_choices": MARITAL_CHOICES,
            "notifications": notifications, 
            "notification_count": notifications.count(), 
        })

@login_required
def investment_plans(request):
    
    notifications = Notification.objects.filter(user=request.user).filter(is_read=False).order_by("-id")[:5]
    plans = Plans.objects.all().order_by("id")

    return render(request, "dashboard/major/plans.html", {
            "employment_statuses": EMPLOYMENT_STATUS,
            "account_types": ACCOUNT_TYPES,
            "all_id_types": PREFERRED_ID_TYPE,
            "citizenship_statuses": CITIZENSHIP_STATUSES,
            "employment_types": EMPLOYMENT_TYPE,
            "marital_choices": MARITAL_CHOICES,
            "notifications": notifications, 
            "notification_count": notifications.count(),
            "plans": plans,
        })


def investment_plan_detail(request, pk):
    try:
        plan = Plans.objects.get(id=pk)
    except Plans.DoesNotExist:
        raise Http404
    
    notifications = Notification.objects.filter(user=request.user).filter(is_read=False).order_by("-id")[:5]
    return render(request, "dashboard/major/plan_detail_payment.html", {
            "notifications": notifications, 
            "notification_count": notifications.count(),
            "plan": plan,
            "payment_options": PAYMENT_TYPES,

        })


def update_payment_information_view(request):
    notifications = Notification.objects.filter(user=request.user).filter(is_read=False).order_by("-id")[:5]
    return render(request, "dashboard/major/update_payment_information_page.html", {
        "notifications": notifications, 
        "notification_count": notifications.count(),
        "payment_options": PAYMENT_TYPES
    })
# -------------------------------------------------------------------------------------





