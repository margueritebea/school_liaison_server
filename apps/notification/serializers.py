from rest_framework import serializers

from .models import UserNotification, Notification, CategoryNotification

from apps.accounts.serializers import ProfileSerializer, ParentSerializer, SenderReceiverSerializer
from apps.school.serializers import StudentSerializer, SchoolYearSerializer

from django.contrib.auth import get_user_model
# from apps.accounts.models import User
User = get_user_model()

class CategoryNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryNotification
        fields = ['id', 'name', 'description']

class NotificationSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(many=True, queryset=CategoryNotification.objects.all())
    reciever_profile = ProfileSerializer(read_only=True)
    sender_profile = ProfileSerializer(read_only=True)
    sender_infos = SenderReceiverSerializer(read_only=True)
    reciever_infos = SenderReceiverSerializer(read_only=True)
    student_infos = StudentSerializer(read_only=True)
    date = serializers.DateField(required=False)
    school_year = SchoolYearSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'sender', 'sender_profile', 'sender_infos', 'reciever_profile', 'reciever_infos', 
            'student', 'student_infos', 'categories', 'message', 'is_read', 'date', 'school_year'
        ]

    def create(self, validated_data):
        categories = validated_data.pop('categories')
        notification = Notification.objects.create(**validated_data)
        notification.categories.set(categories)
        return notification



class UserNotificationSerializer(serializers.ModelSerializer):
    notification = NotificationSerializer(read_only=True)
    student = StudentSerializer(read_only=True)
    user = ParentSerializer(read_only=True)
    school_year = SchoolYearSerializer(read_only=True)

    class Meta:
        model = UserNotification
        fields = ['id', 'user', 'notification', 'student', 'is_read', 'school_year']



