from django.contrib import admin
from django.urls import path, include

from . import views
urlpatterns = [
    # Paypal Paiements
    path('paypal/', include("paypal.standard.ipn.urls")),
    path('payments/paypal/', views.CreatePayPalPaymentView.as_view(), name='create_paypal_payment'),
    path('payments/paypal/capture/', views.CapturePayPalPaymentView.as_view(), name='capture_paypal_payment'),
    path('unpaid-months/<int:student_id>/', views.UnpaidMonthsView.as_view(), name='unpaid-months'),

    # mtn momo
    path('mtn/initier-paiement/', views.initier_paiement),
    path('mtn/verifier-statut-paiement/<str:reference_id>/', views.verifier_statut_paiement),
    path('mtn/get_last_mobile_money_payment/<int:student_id>/', views.get_last_mobile_money_payment, name='get_last_mobile_money_payment'),

    # Orange Money
    path('om/initier-paiement/', views.initier_paiement_orange, name='initier_paiement_orange'),
    path('om/payment/return', views.payment_success, name='payment_success'),
    path('om/payment/cancel', views.payment_cancel, name='payment_cancel'),
    path('om/payment/notification', views.payment_notification, name='payment_notification'),

]
