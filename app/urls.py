from django.urls import path
from . import views

# app_name = 'app'

urlpatterns = [


    # Website Views
    path('', views.home_page, name="home"),
    path('about/', views.about_page, name="about"),
    path('crypto/', views.crypto_page, name="crypto"),
    path('donate/', views.donate_page, name="donate"),
    path('faqs/', views.faqs_page, name="faqs"),
    path('contact/', views.contact, name="contact"),

    # Auth Views
    path('login/', views.login, name="login"),
    path('register/', views.register, name="register"),
    path('logout/', views.LogoutView, name="logout"),
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('password-reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password-reset-complete/', views.password_reset_complete, name='password_reset_complete'),

    # Dashboard Views
    path('dashboard/', views.dashboard_home, name="dashboard_home"),
    path('dashboard/monitor-investment/', views.monitor_investment, name="monitor_investment"),
    path('dashboard/chart-analysis/', views.chart_analysis, name="chart_analysis"),
    path('dashboard/fund-wallet/', views.fund_wallet, name="fund_wallet"),
    path('dashboard/withdraw-fund-wallet/', views.withdraw_fund_wallet, name="withdraw_fund_wallet"),
    path('dashboard/transactions/', views.transactions, name="transactions"),
    path('dashboard/profile/', views.profile_details, name="profile"),
    path('dashboard/settings/', views.profile_settings, name="profile_settings"),
    path('dashboard/investments/', views.investment_create, name="investment_create"),

    path('dashboard/support/', views.support_page, name="support"),
    path('dashboard/notification/', views.notification_page, name="notification"),
    path('dashboard/kyc/', views.update_kyc, name="update_kyc"),
    path('dashboard/investment-plans/', views.investment_plans, name="investment_plans"),
    path('dashboard/investment-plans/<int:pk>/', views.investment_plan_detail, name="investment_plan_detail"),
    path('dashboard/payment-info/', views.update_payment_information_view, name="update_payment_information_view"),
]
