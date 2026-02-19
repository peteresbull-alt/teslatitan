from django.urls import path
from . import views


urlpatterns = [
   
    path('login/', views.login_with_email_api, name="login_with_email_api"),
    path("register/", views.register_api_view, name="api_register"),
    path("update-profile-api/", views.update_profile_api_view, name="update_profile_api_view"),
    path("change-password-api/", views.change_password_api_view, name="change_password_api_view"),
    path("support-api/", views.support_api, name="support_api"),
    path("clear-user-notification/", views.clear_user_notification, name="clear_user_notification"),

    path("verify-user-kyc/", views.KYCAPIView, name="verify_user_kyc"),
    path("funding-account-request-api/", views.funding_account_request_api, name="funding_account_request_api"),
    path("withdrawal-request-api/", views.withdrawal_request_api, name="withdrawal_request_api"),
    path("invetments-create-api/", views.investment_create_request_api, name="investment_create_request_api"),

    
    path("update-payment-information-api/", views.update_payment_information_api, name="update_payment_information_api"),
    path("delete-payment-method/<int:pk>/", views.delete_payment_method_api, name="delete_payment_method_api"),
    path("edit-payment-method/<int:pk>/", views.edit_payment_method_api, name="edit_payment_method_api"),

    path("get-wallet-address/<str:wallet_type>/", views.get_wallet_address, name="get_wallet_address"),

    path('contact/', views.ContactFormView.as_view(), name='contact-form'),
]
