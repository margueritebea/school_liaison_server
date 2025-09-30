# from django.shortcuts import render
from django.contrib.auth import authenticate
# from django.db import transaction
from django.shortcuts import get_object_or_404
# from django.core.exceptions import ObjectDoesNotExist
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta, datetime
# from django.utils.dateparse import parse_date
# import requests


from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics, mixins
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.serializers import ValidationError
from rest_framework.decorators import  permission_classes
from rest_framework import status
from rest_framework.generics import RetrieveAPIView
# from rest_framework.exceptions import PermissionDenied
# from rest_framework.exceptions import NotFound  


from . permissions import IsParent, IsAgent
from . models import PasswordResetAttempt, Profile, User
from . serializers import UserSerializer, SignUpSerializer, ProfileSerializer, ProfilePhotoSerializer, ProfileWithStudentsSerializer



# Authentication Views
def get_auth_for_user(user):
    tokens = RefreshToken.for_user(user)
    return {
        'user': UserSerializer(user).data,
        'tokens': {
            'access': str(tokens.access_token),
            'refresh': str(tokens),
        }
    }    


class SignInView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        identifier = request.data.get('identifier')
        password = request.data.get('password')

        if not identifier or not password:
            return Response({"error": "Identifiant et mot de passe sont requis"}, status=status.HTTP_400_BAD_REQUEST)
        
        if '@' in identifier:
            try:
                user = User.objects.get(email=identifier)
                username = user.username
            except User.DoesNotExist:
                return Response({"error": "Email incorrect"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            username = identifier
        
        user = authenticate(username=username, password=password)

        if not user:
            # return Response(status=401)
            return Response({"error": "Nom d'utilisateur ou mot de passe incorrect"}, status=status.HTTP_401_UNAUTHORIZED)
        
        user_data = get_auth_for_user(user)

        return Response(user_data)

class SignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        new_user = SignUpSerializer(data=request.data)
        new_user.is_valid(raise_exception=True)
        user = new_user.save()

        user_data = get_auth_for_user(user)

        return Response(user_data)

class SendResetCodeByEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "L'adresse email est requise."}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, email=email)
        
        # Vérifier le nombre de tentatives récentes
        attempts_record, created = PasswordResetAttempt.objects.get_or_create(user=user)
        current_time = timezone.now()
        
        # Si plus de 3 tentatives en moins de 1 heure, refuser la nouvelle tentative
        if attempts_record.attempts >= 5 and current_time - attempts_record.timestamp < timedelta(hours=1):
            return Response({"error": "Vous avez dépassé le nombre de tentatives autorisées. Veuillez réessayer plus tard."}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        # Réinitialiser les tentatives après 1 heure
        if current_time - attempts_record.timestamp >= timedelta(hours=1):
            attempts_record.attempts = 0
            attempts_record.timestamp = current_time
        
        # Incrémenter les tentatives
        attempts_record.attempts += 1
        attempts_record.save()

        # Générer un code de réinitialisation aléatoire et définir l'expiration
        reset_code = get_random_string(6, '0123456789')
        user.reset_code = reset_code
        user.reset_code_created_at = timezone.now()  # Enregistrer l'heure de création du code
        user.save()
        from django.conf import settings
        send_mail(
            subject="Réinitialisation de mot de passe",
            message=f"Votre code de réinitialisation est : {reset_code}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )
        
        return Response({"success": "Le code de réinitialisation a été envoyé par email."}, status=status.HTTP_200_OK)

class ConfirmResetCodeByEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        reset_code = request.data.get('code')

        if not all([email, reset_code]):
            return Response({"error": "Tous les champs sont requis."}, status=status.HTTP_400_BAD_REQUEST)
        
        user = get_object_or_404(User, email=email, reset_code=reset_code)
        
        # Vérifiez si le code est valide en fonction de reset_code et reset_code_created_at
        if user.reset_code == reset_code and user.reset_code_created_at:
            # Vérifier si le code a expiré
            expiration_time = user.reset_code_created_at + timedelta(hours=1)  # Durée d'expiration de 1 heure
            if timezone.now() > expiration_time:
                return Response({"error": "Le code de réinitialisation a expiré."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Logique de traitement lorsque le code est valide
            return Response({"success": "Le code est valide."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Code de réinitialisation invalide."}, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordByEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        reset_code = request.data.get('code')
        new_password = request.data.get('new_password')

        if not all([email, reset_code, new_password]):
            return Response({"error": "Tous les champs sont requis."}, status=status.HTTP_400_BAD_REQUEST)
        
        user = get_object_or_404(User, email=email, reset_code=reset_code)
        
        if user:
            user.set_password(new_password)
            user.reset_code = None  # Supprimer le code de réinitialisation après utilisation
            user.save()
            return Response({"success": "Mot de passe réinitialisé avec succès."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Code de réinitialisation invalide."}, status=status.HTTP_400_BAD_REQUEST)

class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        
        # Supprimer les notifications de l'utilisateur
        user_notifications = UserNotification.objects.filter(user=user)
        user_notifications.delete()

        # Supprimer les abonnements de l'utilisateur
        subscriptions = Subscription.objects.filter(parent=user)
        subscriptions.delete()

        # Supprimer les paiement de l'utilisateur
        payments = Payment.objects.filter(parent=user)
        payments.delete()

        # Suppression de l'utilisateur
        user.delete()

        return Response({"detail": "Votre compte a été supprimé avec succès."}, status=status.HTTP_204_NO_CONTENT)

# Profiles View
class ProfileList(generics.ListCreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user

        profile = Profile.objects.filter(user=user).first()

        if profile:
            serializer.save()
        else:
            raise ValidationError("L'utilisateur n'existe pas")

    def get_queryset(self):
        # Récupérer l'utilisateur actuel
        user = self.request.user

        if user:
            return Profile.objects.filter(user=user)
        else:
            # Renvoyer une liste vide si l'agent n'est affecté à aucune école
            return Profile.objects.none()

class ProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

class ProfilePhotoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        serializer = ProfilePhotoSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        serializer = ProfilePhotoSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileStudentView(generics.ListAPIView):
    serializer_class = ProfileWithStudentsSerializer
    permission_classes = [IsAuthenticated, IsParent]

    def get_queryset(self):
        profile_id = self.kwargs.get('profile_id')
        return Profile.objects.filter(pk=profile_id)

class ProfileAddStudent(generics.ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsParent]

    def get_queryset(self):
        queryset = super().get_queryset()
        profile_id = self.kwargs.get('profile_id')
        return queryset.filter(pk=profile_id)
    
    def post(self, request, profile_id):
        # Récupérer le profil existant
        profile = get_object_or_404(Profile, pk=profile_id)

        # Récupérer l'utilisateur lié au profil
        parent = profile.user  # Assurez-vous que le modèle Profile a une relation avec User.

        # Récupérer le numéro de matricule de l'élève à ajouter
        student_id = request.data.get('student')
        if not student_id:
            return Response({"error": "Student matricule is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Récupérer l'élève existant en fonction du numéro de matricule
        student = get_object_or_404(Student, id=student_id)
        # Vérifier si l'étudiant est déjà dans le profil
        if profile.student.filter(id=student.id).exists():
            return Response({"error": "Student is already added to the profile"}, status=status.HTTP_400_BAD_REQUEST)

        # Ajouter l'élève au profil existant
        profile.student.add(student)

        # PROMO ENVOI DES NOTIFICATIONS AUX PARENTS
        # Envoyer les notifications après la souscription
        notifications = Notification.objects.filter(student=student)
        for notification in notifications:
            UserNotification.objects.get_or_create(
                user=parent,
                notification=notification,
                student=student
            )

        # Serializer le profil mis à jour
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RemoveStudentFromProfileView(APIView):
    permission_classes = [IsAuthenticated, IsParent]

    def post(self, request, profile_id, student_id):
        profile = get_object_or_404(Profile, id=profile_id)
        
        # Vérifier que l'utilisateur a le droit de modifier ce profil
        if request.user != profile.user:
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
        
        success = profile.remove_student(student_id)

        if success:
            return Response({"message": "Student removed successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Student not found in profile"}, status=status.HTTP_404_NOT_FOUND)


