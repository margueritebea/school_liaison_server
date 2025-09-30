from django.test import TestCase

import pytest
from . models import User, Profile

# Test User Model
@pytest.mark.django_db
def test_create_user():
    user = User.objects.create_user(
        username='testuser',
        password='password123',
        full_name='Test User',
        phone='123456789',
        role='parent'
    )
    assert user.username == 'testuser'
    assert user.full_name == 'Test User'
    assert user.phone == '123456789'
    assert user.role == 'parent'
    assert user.check_password('password123')

@pytest.mark.django_db
def test_user_profile_creation():
    user = User.objects.create_user(
        username='testuser2',
        password='password123',
        full_name='Test User 2',
        phone='987654321',
        role='agent'
    )
    
    if not hasattr(user, 'profile'):
        profile = Profile.objects.create(user=user)
    profile = Profile.objects.get(user=user)
    assert profile is not None

@pytest.mark.django_db
def test_user_profile_method():
    user = User.objects.create_user(
        username='testuser3',
        password='password123',
        full_name='Test User 3',
        phone='111222333',
        role='parent'
    )
    profile = user.profile
    assert profile.user == user
