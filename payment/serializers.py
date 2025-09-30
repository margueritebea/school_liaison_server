from rest_framework import serializers


from .models import Payment, PayPalPayment


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class PayPalPaymentSerializer(serializers.ModelSerializer):
    payment = PaymentSerializer()

    class Meta:
        model = PayPalPayment
        fields = '__all__'
