
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from django.dispatch import receiver




# School Year Model 
class SchoolYear(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.start_date.year}-{self.end_date.year}"

    class Meta:
        verbose_name_plural = "0. School Years"

# # School Model 
# class School(models.Model):
#     name = models.CharField(max_length=100)
#     address = models.CharField(max_length=255)
#     agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

#     def __str__(self):
#         return f"{self.name} - {self.agent}"
    
#     class Meta:
#         verbose_name_plural = "2. School"

# # Classe Model 
# class Classe(models.Model):
#     school = models.ForeignKey(School, on_delete=models.CASCADE)
#     level = models.CharField(max_length=100,choices=[
#         ('primaire', 'Primaire'),
#         ('college', 'Collège'),
#         ('lycee', 'Lycée')
#     ])
#     name = models.CharField(max_length=100,choices=[
#     ])
#     school_year = models.ForeignKey(SchoolYear, on_delete=models.SET_NULL, null=True, blank=True)

#     def __str__(self):
#         return f"{self.name} - {self.school}"
    
#     class Meta:
#         verbose_name_plural = "3. Classe" 

# Student Model
class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    matricule = models.CharField(max_length=100, null=True, unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to='student_images/', blank=True, null=True, default="default.jpg")
    classe = models.ForeignKey(Classe, on_delete=models.SET_NULL, null=True, blank=True)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.matricule} - {self.first_name} {self.last_name}"
    
    def get_active_subscriptions(self):
        return self.subscription_set.filter(status='completed', end_date__gte=timezone.now().date())
    
    @property
    def classe_infos(self):
        classe_infos = self.classe
        return classe_infos
    
    class Meta:
        verbose_name_plural = "4. Student"

# Head Teacher Model
class Teacher(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length = 100)
    classe = models.ForeignKey(Classe, on_delete=models.SET_NULL, null=True, blank=True)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.classe} {self.phone}" 
    
    @property
    def classe_infos(self):
        classe_infos = self.classe  
        return classe_infos
    
    class Meta:
        verbose_name_plural = "5. Teacher"



# Category Notification Model 
# class CategoryNotification(models.Model):
#     name = models.CharField(max_length=100)
#     description = models.TextField()

#     def __str__(self):
#         return self.name
#     class Meta:
#         verbose_name_plural = "6. Category Notification"

# # Notification Model 
# class Notification(models.Model):
#     user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="user")
#     sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="sender")
#     student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="student")
#     categories = models.ManyToManyField(CategoryNotification, related_name="notifications")
#     message = models.TextField()
#     is_read = models.BooleanField(default=False)
#     date = models.DateField()
#     school_year = models.ForeignKey(SchoolYear, on_delete=models.SET_NULL, null=True, blank=True)

#     def __str__(self):
#         return f"{self.sender} | {self.student} {self.message}"

#     def create_user_notifications(self):
#         parents = self.student.profile_set.filter(user__role='parent')
#         # for parent_profile in parents:
#         #     # Récupérer la dernière souscription
#         #     last_subscription = parent_profile.user.subscription_set.filter(student=self.student).order_by('-end_date').first()
#         #     # Vérifier si la dernière souscription est active
#         #     if last_subscription and last_subscription.status:
#         #         UserNotification.objects.create(
#         #             user=parent_profile.user,
#         #             notification=self,
#         #             student=self.student,
#         #         )
#         for parent_profile in parents:
#             # Vérifier si la dernière souscription est active
#             UserNotification.objects.create(
#                 user=parent_profile.user,
#                 notification=self,
#                 student=self.student,
#             )

#     @property
#     def sender_profile(self):
#         sender_profile = Profile.objects.get(user=self.sender)
#         return sender_profile

#     @property
#     def student_infos(self):
#         student_infos = self.student
#         return student_infos

#     @property
#     def category_infos(self):
#         category_infos = self.categories.all()
#         return category_infos

#     class Meta:
#         verbose_name_plural = "7. Notification"

# # User Notification Model 
# class UserNotification(models.Model):
#     user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
#     notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
#     student = models.ForeignKey(Student, on_delete=models.CASCADE)
#     is_read = models.BooleanField(default=False)
#     school_year = models.ForeignKey(SchoolYear, on_delete=models.SET_NULL, null=True, blank=True)

#     def __str__(self):
#         return f"{self.user.full_name} - {self.student}"

#     def save(self, *args, **kwargs):
#         super().save(*args, **kwargs)

#     class Meta:
#         verbose_name_plural = "7.1 User Notification"
#         unique_together = ('user', 'notification', 'student')    

# Student Statistics Model
# class StudentStatistics(models.Model):
#     student = models.ForeignKey(Student, on_delete=models.CASCADE)
#     school_year = models.ForeignKey(SchoolYear, on_delete=models.SET_NULL, null=True, blank=True)
#     absence = models.IntegerField(default=0)
#     absence_autorisee = models.IntegerField(default=0)
#     presence = models.IntegerField(default=0)
#     mauvaise_conduite = models.IntegerField(default=0)
#     bonne_conduite = models.IntegerField(default=0)
#     participation_active = models.IntegerField(default=0)
#     participation_moyenne = models.IntegerField(default=0)
#     participation_faible = models.IntegerField(default=0)
#     bonne_moyenne = models.IntegerField(default=0)
#     mauvaise_moyenne = models.IntegerField(default=0)

#     def __str__(self):
#         return f"Statistiques de {self.student} pour {self.school_year}"

#     class Meta:
#         verbose_name_plural = "8. Student Statistics"
#         unique_together = ('student', 'school_year')

# # Signal pour mettre à jour les statistiques après la sauvegarde d'une notification
# @receiver(post_save, sender=Notification)
# def update_student_statistics(sender, instance, created, **kwargs):
#     if created:
#         statistics, _ = StudentStatistics.objects.get_or_create(
#             student=instance.student,
#             school_year=instance.school_year
#         )
#         for category in instance.categories.all():
#             if category.name == "présence en classe":
#                 statistics.presence += 1
#             elif category.name == "absence en classe":
#                 statistics.absence += 1
#             elif category.name == "absence autorisée":
#                 statistics.absence_autorisee += 1
#             elif category.name == "bonne conduite à l'école":
#                 statistics.bonne_conduite += 1
#             elif category.name == "mauvaise conduite à l'école":
#                 statistics.mauvaise_conduite += 1
#             elif category.name == "participation active en classe":
#                 statistics.participation_active += 1
#             elif category.name == "participation moyenne en classe":
#                 statistics.participation_moyenne += 1
#             elif category.name == "participation faible en classe":
#                 statistics.participation_faible += 1
#             elif category.name == "bonne moyenne aux tests/évaluations":
#                 statistics.bonne_moyenne += 1
#             elif category.name == "mauvaise moyenne aux tests/évaluations":
#                 statistics.mauvaise_moyenne += 1
#         statistics.save()

# # Subscription Model
# def get_end_of_month(start_date):
#     next_month = start_date.replace(day=28) + timedelta(days=4)
#     return next_month - timedelta(days=next_month.day)

# class Subscription(models.Model):
#     parent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
#     student = models.ForeignKey(Student, on_delete=models.CASCADE)
#     num_months = models.IntegerField()
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     start_date = models.DateField(default=timezone.now)
#     end_date = models.DateField()
#     payment_method = models.CharField(max_length=50, choices=[
#         ('paypal', 'PayPal'),
#         ('orange_money', 'Orange Money'),
#         ('mobile_money', 'Mobile Money'),
#         ('visa', 'Visa')
#     ], default='paypal')
#     status = models.BooleanField(default=True)  # True si la souscription est active, False sinon

#     def __str__(self):
#         return f"Subscription for {self.student.matricule} by {self.parent.full_name}"

#     def save(self, *args, **kwargs):
#         if not self.start_date:
#             self.start_date = timezone.now().date()
#         if not self.end_date:
#             end_date = self.start_date
#             for _ in range(self.num_months):
#                 end_date = get_end_of_month(end_date)
#                 end_date += timedelta(days=1)
#             self.end_date = end_date - timedelta(days=1)
#         self.status = self.end_date > timezone.now().date()  # Mise à jour du statut
#         super().save(*args, **kwargs)
    
#     class Meta:
#         verbose_name_plural = "9. Subscription"

# # Payment Model
# class Payment(models.Model):
#     subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
#     parent = models.ForeignKey(User,  on_delete=models.SET_NULL, null=True, blank=True)
#     student = models.ForeignKey(Student,  on_delete=models.SET_NULL, null=True, blank=True)
#     payment_method = models.CharField(max_length=50, choices=[
#         ('paypal', 'PayPal'),
#         ('orange_money', 'Orange Money'),
#         ('mobile_money', 'Mobile Money'),
#         ('visa', 'Visa')
#     ])
#     num_months = models.IntegerField()
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     status = models.CharField(max_length=50, choices=[
#         ('pending', 'Pending'),
#         ('completed', 'Completed'),
#         ('cancelled', 'Cancelled')
#     ], default='pending')
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.parent} - {self.student} - {self.amount}"
    
#     class Meta:
#         verbose_name_plural = "10. Payment"

# # PayPalPayment Model
# class PayPalPayment(models.Model):
#     payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='paypal_details')
#     paypal_order_id = models.CharField(max_length=100)

#     def __str__(self):
#         return f"PayPal Payment with order ID {self.paypal_order_id}"

# # MobileMoneyPayment Model
# class MobileMoneyPayment(models.Model):
#     payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='mtn_details')
#     reference_id = models.CharField(max_length=100)

#     def __str__(self):
#         return f"MTN Mobile Money Payment with reference ID {self.reference_id}"

# # OrangeMoneyPayment Model
# class OrangeMoneyPayment(models.Model):
#     payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='orange_money_details')
#     order_id = models.CharField(max_length=100)
#     pay_token = models.CharField(max_length=200, default="")
#     payment_url = models.CharField(max_length=200, default="")
#     notif_token = models.CharField(max_length=200, default="")

#     def __str__(self):
#         return f"Orange Money Payment with transaction ID {self.order_id}"

# class AppVersion(models.Model):
#     platform = models.CharField(max_length=10, choices=[('android', 'Android'), ('ios', 'iOS')])
#     current_version = models.CharField(max_length=10)
#     minimum_required_version = models.CharField(max_length=10)
#     update_url = models.URLField()
#     created_at = models.DateTimeField(auto_now_add=True)