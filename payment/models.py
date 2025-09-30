from django.db import models

from django.utils import timezone
from datetime import timedelta
# Create your models here.

# Subscription Model
def get_end_of_month(start_date):
    next_month = start_date.replace(day=28) + timedelta(days=4)
    return next_month - timedelta(days=next_month.day)

class Subscription(models.Model):
    parent = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True)
    student = models.ForeignKey("school.Student", on_delete=models.CASCADE)
    num_months = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField()
    payment_method = models.CharField(max_length=50, choices=[
        ('paypal', 'PayPal'),
        ('orange_money', 'Orange Money'),
        ('mobile_money', 'Mobile Money'),
        ('visa', 'Visa')
    ], default='paypal')
    status = models.BooleanField(default=True)  # True si la souscription est active, False sinon

    def __str__(self):
        return f"Subscription for {self.student.matricule} by {self.parent.full_name}"

    def save(self, *args, **kwargs):
        if not self.start_date:
            self.start_date = timezone.now().date()
        if not self.end_date:
            end_date = self.start_date
            for _ in range(self.num_months):
                end_date = get_end_of_month(end_date)
                end_date += timedelta(days=1)
            self.end_date = end_date - timedelta(days=1)
        self.status = self.end_date > timezone.now().date()  # Mise à jour du statut
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name_plural = "9. Subscription"

# Payment Model
class Payment(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    parent = models.ForeignKey("accounts.User",  on_delete=models.SET_NULL, null=True, blank=True)
    student = models.ForeignKey("school.Student",  on_delete=models.SET_NULL, null=True, blank=True)
    payment_method = models.CharField(max_length=50, choices=[
        ('paypal', 'PayPal'),
        ('orange_money', 'Orange Money'),
        ('mobile_money', 'Mobile Money'),
        ('visa', 'Visa')
    ])
    num_months = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.parent} - {self.student} - {self.amount}"
    
    class Meta:
        verbose_name_plural = "10. Payment"

# PayPalPayment Model
class PayPalPayment(models.Model):
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='paypal_details')
    paypal_order_id = models.CharField(max_length=100)

    def __str__(self):
        return f"PayPal Payment with order ID {self.paypal_order_id}"

# MobileMoneyPayment Model
class MobileMoneyPayment(models.Model):
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='mtn_details')
    reference_id = models.CharField(max_length=100)

    def __str__(self):
        return f"MTN Mobile Money Payment with reference ID {self.reference_id}"

# OrangeMoneyPayment Model
class OrangeMoneyPayment(models.Model):
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='orange_money_details')
    order_id = models.CharField(max_length=100)
    pay_token = models.CharField(max_length=200, default="")
    payment_url = models.CharField(max_length=200, default="")
    notif_token = models.CharField(max_length=200, default="")

    def __str__(self):
        return f"Orange Money Payment with transaction ID {self.order_id}"

class AppVersion(models.Model):
    platform = models.CharField(max_length=10, choices=[('android', 'Android'), ('ios', 'iOS')])
    current_version = models.CharField(max_length=10)
    minimum_required_version = models.CharField(max_length=10)
    update_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
