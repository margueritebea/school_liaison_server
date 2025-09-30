from django.contrib import admin

from .models import UserNotification, CategoryNotification, Notification

@admin.register(CategoryNotification)
class CategoryNotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'student', 'date']

@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'notification', 'student', 'is_read']

