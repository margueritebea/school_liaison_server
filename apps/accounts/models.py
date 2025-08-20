from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from django.dispatch import receiver

# from apps.school.models import Student

# User Model 
class User(AbstractUser):
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=100, unique=True)
    email = models.EmailField(null=True, blank=True)
    role = models.CharField(max_length=50, choices=[
        ('parent', 'Parent'),
        ('agent', 'Agent')
    ], default='parent')
    reset_code = models.CharField(max_length=6, blank=True, null=True)
    reset_code_created_at = models.DateTimeField(null=True, blank=True)

    def clean(self):
        if self.email:
            if User.objects.exclude(pk=self.pk).filter(email=self.email).exists():
                raise ValidationError({'email': 'Cet email est déjà utilisé.'})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def profile(self):
        profile = Profile.objects.get(user=self)
        return profile
    
    class Meta:
        verbose_name_plural = "1. User"

class PasswordResetAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    attempts = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.user.email} - {self.attempts} attempts'
    
    @staticmethod
    def cleanup_expired_attempts(expiry_hours=24):
        expiry_date = timezone.now() - timedelta(hours=expiry_hours)
        PasswordResetAttempt.objects.filter(timestamp__lt=expiry_date).delete()
    
    class Meta:
        verbose_name_plural = "1.1 Pwd Reset Attempts"


# Profile Model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # student = models.ManyToManyField(Student, blank=True)
    image = models.ImageField(upload_to="user_images/", default="default.jpg")

    class Meta:
        verbose_name_plural = "1.2 Profile"
    
    # def remove_student(self, student_id):
    #     """
    #     Remove a student from the profile's student list.
    #     """
    #     try:
    #         student = self.student.get(id=student_id)
    #         self.student.remove(student)
    #         return True
    #     except Student.DoesNotExist:
    #         return False

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)