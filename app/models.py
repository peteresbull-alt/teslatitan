from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from .managers import CustomUserManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

import random
from datetime import datetime, timedelta

import string
from django.db.models.signals import post_save
from django.dispatch import receiver

from cloudinary.models import CloudinaryField
# Create your models here.

PAYMENT_TYPES = [
    ("WALLET", "WALLET"),
    ("BTC", "BTC"),
    ("ETH", "ETH"),
    ("CASH APP", "CASH APP"),
    ("PAYPAL", "PAYPAL")
]


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model for the broker app where email is the unique identifier for authentication.
    """
    GENDER_CHOICES = [
        ("Male", 'Male'),
        ("Female", 'Female'),
    ]
    PROGRAM_TYPES = [
        ("Short-Term", 'Short-Term'),
        ("Long-Term", 'Long-Term'),
    ]

    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(max_length=50, blank=False)  # Required
    last_name = models.CharField(max_length=50, blank=False)   # Required
    phone_number = models.CharField(max_length=15, unique=True, blank=False)  # Required
    date_of_birth = models.DateField(blank=True, null=True)

    preferred_currency = models.CharField(max_length=100, blank=True, null=True, default="$")

    profile_image = CloudinaryField(resource_type='raw', blank=True, null=True)

    address = models.TextField(blank=True, null=True)  
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)


    postal_code = models.CharField(max_length=100, blank=True, null=True)
    gender =  models.CharField(max_length=100, blank=True, null=True, choices=GENDER_CHOICES, default="Male")


    user_password_in_text = models.CharField(max_length=100, blank=True, null=True)

    annual_income = models.DecimalField(verbose_name="Annual Income", max_digits=12, decimal_places=2, default=0.00)
    citizenship_status = models.CharField(max_length=50, choices=[
        ('US Citizen', 'US Citizen'), 
        ('Non-US Citizen', 'Non-US Citizen')
    ], default='Non-US Citizen')
    
    # User Balances
    capital = models.DecimalField(verbose_name="Capital", max_digits=12, decimal_places=2, default=0.00)
    roi = models.DecimalField(verbose_name="ROI", max_digits=12, decimal_places=2, default=0.00)
    bonus = models.DecimalField(verbose_name="Bonus", max_digits=12, decimal_places=2, default=0.00)
    investment = models.DecimalField(verbose_name="Investment", max_digits=12, decimal_places=2, default=0.00)
    # program_bonus = models.DecimalField(verbose_name="Bonus", max_digits=12, decimal_places=2, default=0.00)

    program_type = models.CharField(max_length=100, blank=True, null=True, choices=PROGRAM_TYPES, default="Short-Term")

    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # User has verified KYC
    # is_verified = models.BooleanField(verbose_name="KYC Verified", default=False)

    has_verified_kyc = models.BooleanField(verbose_name="User is verified", default=False, help_text="Tick if user has undergone KYC Verification and has been approved.")
    has_submitted_kyc = models.BooleanField(help_text="This means that user has submitted verification for KYC", default=False, )


    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']


    @property
    def available_balance(self):
        return self.capital + self.roi



    @property
    def get_profile_image_url(self):
        if self.profile_image:
            return self.profile_image.url
        else:
            # Change this later
            return 'https://res.cloudinary.com/daf9tr3lf/image/upload/v1725024497/undraw_profile_male_oovdba.svg'
        
    @property
    def get_user_fullname(self):
        return str(self.first_name).capitalize() + " " + str(self.last_name).capitalize()


    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name_plural = "Users"
        verbose_name = "User"


class KYC(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    marital_choice = models.CharField(max_length=100, blank=True, null=True)
    number_of_dependents = models.IntegerField(default=0)
    employment_status = models.CharField(max_length=100, blank=True, null=True)
    employment_type = models.CharField(max_length=100, blank=True, null=True)
    citizenship_status = models.CharField(max_length=100, blank=True, null=True)
    ssn = models.CharField(max_length=100, blank=True, null=True)
    tax_identity_number = models.CharField(max_length=100, blank=True, null=True)
    government_id_type = models.CharField(max_length=100, blank=True, null=True)
    government_id_number = models.CharField(max_length=100, blank=True, null=True)
    proof_of_employment = CloudinaryField(resource_type='raw', blank=True, null=True)
    proof_of_income = CloudinaryField(resource_type='raw', blank=True, null=True)
    front_id_image = CloudinaryField(resource_type='raw', blank=True, null=True)
    back_id_image = CloudinaryField(resource_type='raw', blank=True, null=True)
    image_holding_id = CloudinaryField(resource_type='raw', blank=True, null=True)


    def __str__(self):
        return self.user.email + " " + "KYC Details."
    
    class Meta:
        verbose_name_plural = "KYC"
        verbose_name = "KYC"




class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ("danger", "danger"),
        ("success", "success"),
        ("warning", "warning")
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=False, null=False)
    message = models.TextField()
    notification_type = models.CharField(max_length=100, choices=NOTIFICATION_TYPES, verbose_name="Notification Type", help_text="Select the Notification Type. ")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.email} - {self.title}"

    class Meta:
        verbose_name_plural = "Notification"
        verbose_name = "Notifications"


class Support(models.Model):
    STATUS = [
        ("Pending", "Pending"),
        ("Fulfilled", "Fulfilled"),
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.CharField(max_length=400, blank=True, null=False)
    description = models.TextField(max_length=400, blank=True, null=False)
    image = CloudinaryField(resource_type='raw', blank=True, null=True)
    status = models.CharField(max_length=400, blank=True, null=False, choices=STATUS, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Support"
        verbose_name = "Support"

    def __str__(self):
        return f"Support for {self.user.email} - {self.subject}"


class Payment(models.Model):
    
    TRANSACTION_TYPES = (
        ('FUNDING', 'FUNDING'),
        ('WITHDRAWAL', 'WITHDRAWAL'),
    )
    STATUS = [
        ("Pending", "Pending"),
        ("Success", "Success"),
    ]
    
    date = models.DateField(auto_now_add=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    transaction_type = models.CharField(max_length=400, blank=True, null=False, choices=TRANSACTION_TYPES)
    amount = models.IntegerField(blank=True, null=True)
    confirmation_receipt = CloudinaryField(resource_type='raw', blank=True, null=True)
    payment_method = models.CharField(max_length=400, blank=True, null=True)
    wallet = models.CharField(max_length=400, blank=True, null=True)
    withdraw_source = models.CharField(max_length=400, blank=True, null=True)

    status = models.CharField(max_length=400, blank=True, null=False, default="Pending", choices=STATUS)

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

    def __str__(self) -> str:
        return f"Transaction by {self.user.email} ---- {self.transaction_type}"



class Investment(models.Model):
    INVESTMENT_TYPES = [
        ("Basic Plan", "Basic Plan"),
        ("Standard Plan", "Standard Plan"),
        ("Premium Plan", "Premium Plan"),
        ("Elite Plan", "Elite Plan"),
    ]

    STATUS = [
        ("Pending", "Pending"),
        ("Successful", "Successful"),
    ]

    date = models.DateField(auto_now_add=True)
    amount = models.IntegerField(blank=True, null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name="investments")
    investment_type = models.CharField(max_length=400, blank=True, null=True, choices=INVESTMENT_TYPES)
    status = models.CharField(max_length=400, blank=True, null=False, default="Pending", choices=STATUS)

    class Meta:
        verbose_name = "Investment"
        verbose_name_plural = "Investments"

    def __str__(self):
        return f"{self.user.email} ---- {self.investment_type}"

class AdminPaymentMethod(models.Model):
    
    payment_type =  models.CharField(max_length=400, blank=True, null=False, choices=PAYMENT_TYPES)
    payment_address = models.CharField(max_length=400, blank=True, null=False)

    def __str__(self) -> str:
        return f"{self.payment_type}"


class Plans(models.Model):
    plan_name = models.CharField(max_length=100, default="Universal Plan", blank=False, null=False)
    minimum_deposit = models.DecimalField(verbose_name="Minimum Deposit", max_digits=12, decimal_places=2, default=0.00)
    maximum_deposit = models.DecimalField(verbose_name="Maximum Deposit", max_digits=12, decimal_places=2, default=0.00)
    term_duration = models.CharField(max_length=100, default="10 Days", blank=False, null=False)
    payout_term = models.CharField(max_length=100, default="Term Basis", blank=False, null=False)
    capital_return = models.CharField(max_length=100, default="End of Term", blank=False, null=False)
    percentage_return = models.CharField(max_length=100, default="130%", blank=False, null=False)

    def __str__(self):
        return f"Investment Plan - {self.plan_name}".upper()
    
    class Meta:
        verbose_name = "Investment Plan"
        verbose_name_plural = "Investment Plans"


class CustomerPaymentInformation(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    payment_type =  models.CharField(max_length=400, blank=True, null=False, choices=PAYMENT_TYPES)
    payment_address = models.CharField(max_length=400, blank=True, null=False)

    def __str__(self):
        return f"Customer Payment Information for - {self.user.email}" 
    
    class Meta:
        verbose_name = "Customer Payment Information"
        verbose_name_plural = "Customer Payment Information"


class AdminWallet(models.Model):
    wallet_type =  models.CharField(max_length=400, blank=True, null=False)
    wallet_address = models.CharField(max_length=400, blank=True, null=False)

    def __str__(self):
        return f"{self.wallet_type} --- {self.wallet_address}"
    
    class Meta:
        verbose_name = "Admin Wallet"
        verbose_name_plural = "Admin Wallets"




