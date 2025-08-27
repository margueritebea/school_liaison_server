from django.contrib import admin

from .models import Subscription, Payment, PayPalPayment, AppVersion, MobileMoneyPayment, OrangeMoneyPayment

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_editable = ['status']
    list_display = ['id', 'parent', 'student', 'num_months', 'amount', 'start_date', 'end_date', 'payment_method', 'status']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'parent', 'student', 'payment_method', 'amount', 'created_at', 'status']

@admin.register(PayPalPayment)
class PayPalPaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'payment', 'paypal_order_id']

@admin.register(MobileMoneyPayment)
class MobileMoneyPaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'payment', 'reference_id']


@admin.register(OrangeMoneyPayment)
class OrangeMoneyPaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'payment', 'order_id']


@admin.register(AppVersion)
class AppVersionAdmin(admin.ModelAdmin):
    list_display = ['id', 'platform', 'current_version', 'minimum_required_version', 'update_url', 'created_at']
