from rest_framework import serializers

# from .models import

class UserNotificationSerializer(serializers.ModelSerializer):
    notification = NotificationSerializer(read_only=True)
    student = StudentSerializer(read_only=True)
    user = ParentSerializer(read_only=True)
    school_year = SchoolYearSerializer(read_only=True)

    class Meta:
        model = UserNotification
        fields = ['id', 'user', 'notification', 'student', 'is_read', 'school_year']



class CategoryNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryNotification
        fields = ['id', 'name', 'description']
