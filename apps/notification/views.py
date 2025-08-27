# from django.shortcuts import render
from django.db import transaction


from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics, mixins
from rest_framework.decorators import api_view
from rest_framework.views import APIView

from .models import CategoryNotification, Notification
from . serializers import CategoryNotificationSerializer, NotificationSerializer, UserNotificationSerializer
from apps.accounts.permissions import IsAgent, IsParent
from apps.school.models import SchoolYear, School, Student, Classe # Subscription



# from django.contrib.auth import authenticate

from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from django.shortcuts import get_object_or_404
# from django.core.exceptions import
from rest_framework import status
from datetime import timedelta, datetime

from django.utils.dateparse import parse_date

from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import  permission_classes
from rest_framework.exceptions import NotFound  

from apps.accounts.permissions import IsParent, IsAgent



# Notifications views
class CategorieNotificationView(generics.ListAPIView):
    serializer_class = CategoryNotificationSerializer
    queryset = CategoryNotification.objects.all()
    permission_classes = [IsAuthenticated]

# Vue pour permettre à l'agent d'envoyer les notifications
class NotificationCreateView(generics.CreateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, IsAgent]

    @transaction.atomic
    def perform_create(self, serializer):
        agent = self.request.user

        if agent.role != 'agent':
            raise ValidationError("Vous devez être un agent pour envoyer des notifications.")

        school = School.objects.filter(agent=agent).first()
        if not school:
            raise ValidationError("L'agent n'est affecté à aucune école.")

        student_id = self.request.data.get('student')
        category_ids = self.request.data.get('categories')
        notification_message = self.request.data.get('message')
        notification_date_str = self.request.data.get('date')
        school_year_id = self.request.data.get('school_year_id')

        if not student_id:
            raise ValidationError("L'Id de l'élève est obligatoire.")

        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            raise ValidationError("Aucun élève trouvé avec ce matricule.")

        categories = CategoryNotification.objects.filter(id__in=category_ids)
        if not categories:
            raise ValidationError("Aucune catégorie trouvée.")

        if notification_date_str:
            try:
                notification_date = parse_date(notification_date_str)
                if notification_date is None:
                    raise ValueError
            except ValueError:
                raise ValidationError("Format de date invalide. Utilisez le format YYYY-MM-DD.")
        else:
            notification_date = datetime.now().date()

        try:
            school_year = SchoolYear.objects.get(id=school_year_id)
        except SchoolYear.DoesNotExist:
            raise ValidationError("L'année scolaire n'existe pas.")

        with transaction.atomic():
            notification = Notification.objects.create(
                user=agent,
                sender=agent,
                student=student,
                message=notification_message,
                date=notification_date,
                school_year=school_year
            )
            notification.categories.set(categories)
            notification.create_user_notifications()
            update_student_statistics(Notification, notification, created=True)

# Vue pour permettre à l'agent de voir toutes les notifications envoyées par classe
class AgentStudentsNotificationsByClassList(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, IsAgent]

    def get_queryset(self):
        user = self.request.user
        latest_school_year = SchoolYear.objects.latest('end_date')
        class_id = self.request.query_params.get('class_id', None)
        student_id = self.request.query_params.get('student_id', None)

        if student_id:
            notifications = Notification.objects.filter(sender=user, student_id=student_id, school_year=latest_school_year).order_by("-date")
        elif class_id:
            classe = get_object_or_404(Classe, id=class_id)
            students_in_class = classe.student_set.all()
            latest_notifications = []
            for student in students_in_class:
                latest_notification = Notification.objects.filter(sender=user, student=student, school_year=latest_school_year).order_by('-date').first()
                if latest_notification:
                    latest_notifications.append(latest_notification)
            notifications = sorted(latest_notifications, key=lambda x: x.date, reverse=True)
        else:
            students = Student.objects.all()
            latest_notifications = []
            for student in students:
                latest_notification = Notification.objects.filter(sender=user, student=student, school_year=latest_school_year).order_by('-date').first()
                if latest_notification:
                    latest_notifications.append(latest_notification)
            notifications = sorted(latest_notifications, key=lambda x: x.date, reverse=True)

        return notifications

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset:
            raise NotFound(detail="Aucune notification trouvée.")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

# Vue pour permettre à l'agent de voir toutes les notifications envoyées par élève
class AgentNotificationsByStudent(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, IsAgent]

    def get_queryset(self):
        user = self.request.user
        student_id = self.request.query_params.get('student_id')
        
        if not student_id:
            raise ValidationError("L'ID de l'élève est requis.")

        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            raise NotFound("L'élève spécifié n'existe pas.")

        latest_school_year = SchoolYear.objects.latest('end_date')
        return Notification.objects.filter(sender=user, student=student, school_year=latest_school_year).order_by('-date')[:6]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            raise NotFound(detail="Aucune notification trouvée pour cet élève.")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

# Parents student Notifications Views 
class ParentNotificationsByStudent(generics.ListAPIView):
    serializer_class = UserNotificationSerializer
    permission_classes = [IsAuthenticated, IsParent]

    def get_queryset(self):
        user = self.request.user
        student_id = self.kwargs.get('student_id')

        if not student_id:
            raise ValidationError("L'ID de l'élève est requis.")

        student = get_object_or_404(Student, pk=student_id)

        # Vérifiez si le parent a une souscription active pour cet élève
        #last_subscription = Subscription.objects.filter(parent=user, student=student).order_by('-end_date').first()
        #if not last_subscription or not last_subscription.status:
        #    raise PermissionDenied("Vous n'avez pas de souscription active pour voir les notifications de cet élève.")

        return UserNotification.objects.filter(user=user, student=student).distinct().order_by('-notification__date')

class ParentNotificationDetail(APIView):
    permission_classes = [IsAuthenticated, IsParent]

    def get(self, request, user_notification_id):
        user = request.user
        try:
            user_notification = UserNotification.objects.get(id=user_notification_id, user=user)
        except UserNotification.DoesNotExist:
            raise PermissionDenied("Vous n'avez pas accès à cette notification ou elle n'existe pas.")

        # Vérifiez si le parent a une souscription active pour cet élève
        #last_subscription = Subscription.objects.filter(parent=user, student=user_notification.student).order_by('-end_date').first()
        #if not last_subscription or not last_subscription.status:
        #    raise PermissionDenied("Vous n'avez pas de souscription active pour voir cette notification.")

        # Marquer la notification comme lue
        user_notification.is_read = True
        user_notification.save()

        serializer = UserNotificationSerializer(user_notification)
        return Response(serializer.data)

class UnreadNotificationCountView(APIView):
    permission_classes = [IsAuthenticated, IsParent]

    def get(self, request):
        user = request.user

        # Récupérer les élèves pour lesquels le parent a une souscription active
        # active_subscriptions = Subscription.objects.filter(parent=user, status=True)
        # active_students = [subscription.student for subscription in active_subscriptions]
        # Compter les notifications non lues pour ces élèves
        # unread_count = UserNotification.objects.filter(user=user, student__in=active_students, is_read=False).count()

        # Récupérer tous les élèves associés à ce parent
        students = Student.objects.filter(profile__user=user)
        # Compter les notifications non lues pour ces élèves
        unread_count = UserNotification.objects.filter(user=user, student__in=students, is_read=False).count()

        return Response({"unread_count": unread_count})
    
class UnreadNotificationsByStudentView(APIView):
    permission_classes = [IsAuthenticated, IsParent]

    def get(self, request):
        user = request.user

        # Récupérer les élèves associés au parent
        students = Student.objects.filter(profile__user=user)

        # Initialiser un dictionnaire pour les résultats
        unread_notifications = {}

        # Parcourir chaque élève et compter les notifications non lues
        for student in students:
            unread_count = UserNotification.objects.filter(
                user=user, student=student, is_read=False
            ).count()
            unread_notifications[student.matricule] = unread_count

        return Response({"unread_notifications": unread_notifications})
