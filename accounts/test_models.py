from django.test import TestCase
from django.core.exceptions import ValidationError

from accounts.models import User, Profile

class UserModelTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            full_name='Test User',
            phone='1234567890',
            email='test@mail.gn',
            username='testuser',
            password='password123',
            role='parent'
        )
    
    def test_user_creation(self):
        self.assertEqual(self.user.full_name, 'Test User')
        self.assertEqual(self.user.phone, '1234567890')
        self.assertEqual(self.user.email, 'test@mail.gn')
        self.assertEqual(self.user.username, 'testuser')
        self.assertTrue(self.user.check_password('password123'))
        self.assertEqual(self.user.role, 'parent')
    
    def test_email_uniqueness(self):
        with self.assertRaises(ValidationError):
            user2 = User(
                full_name='Another User',
                phone='0987654321',
                email='test@mail.gn',  # Duplicate email
                username='anotheruser',
                password='password123',
                role='agent'
            )
            user2.full_clean()  # This will trigger the validation

        
    # def test_phone_uniqueness(self):
    #     with self.assertRaises(ValidationError):
    #         user2 = User(
    #             full_name='Another User',
    #             phone='1234567890',
    #             email="test1@mail2.mail",
    #             username='anotheruser',
    #             password='password123',
    #             role='agent'
    #         )
    #         user2.full_clean()  # This will trigger the validation
    
    def test_clean_method(self):
        self.user2 = User(
                full_name='Another User',
                phone='1234567890',
                email='test@mail.gn',
                username='anotheruser',
                password='password123',
                role='agent'
            )
        self.assertRaises(ValidationError, self.user2.clean)
"""
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
        verbose_n
"""