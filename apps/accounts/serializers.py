from rest_framework import serializers

from .models import User, Profile, PasswordResetAttempt


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'full_name', 'phone', 'email', 'password']
        extra_kwargs = {
            'password': {
                'write_only': True
            },
            'email': {
                'required': False,
                'allow_null': True,
                'allow_blank': True
            }
        }
    
    def validate_email(self, value):
        if value:  
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError("Cet email est déjà utilisé.")
            return value.lower()
        return None  
    
    def create(self, validated_data):
        full_name   = validated_data['full_name'].lower()
        username    = validated_data['username'].lower()
        phone       = validated_data['phone'].lower()
        email       = validated_data.get('email', None)  
        
        user = User.objects.create(
            full_name=full_name,
            username=username,
            phone=phone,
            email=email
        )
        
        password = validated_data['password']
        user.set_password(password)
        user.save()
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'full_name', 'phone', 'email', 'role']

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'user', 'student', 'image']




class ProfilePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'image']

    def update(self, instance, validated_data):
        image = validated_data.get('image', instance.image)
        if image:
            instance.image = image
        instance.save()
        return instance