from django.contrib import admin

# Register your models here.


class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'full_name', 'phone', 'role']

class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'image']

class PasswordResetAttemptAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'timestamp', 'attempts']