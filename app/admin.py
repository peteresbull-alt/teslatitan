from django.contrib import admin
from .models import (
    KYC,
    Transaction,
    CustomUser,
    Notification,
    Support,
    # Plans,
    CustomerPaymentInformation,
    AdminWallet,
    Investment,
)

# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Transaction)
admin.site.register(Notification)
admin.site.register(KYC)
admin.site.register(Support)
# admin.site.register(Plans)
admin.site.register(CustomerPaymentInformation)
admin.site.register(AdminWallet)
admin.site.register(Investment)

