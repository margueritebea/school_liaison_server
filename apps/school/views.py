from django.shortcuts import render
from core.models import Classe, School, Student, Teacher, SchoolYear, StudentStatistics, 

from . serializers import (
    ProfileWithStudentsSerializer, UserSerializer, ClasseSerializer, 
    SchoolSerializer, StudentSerializer, TeacherSerializer, StudentStatisticSerializer, 
    StudentPhotoSerializer, SchoolYearSerializer, StudentStatisticsDetailSerializer
)
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, mixins
from rest_framework.serializers import ValidationError
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta, datetime
from django.utils.dateparse import parse_date
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import  permission_classes
from rest_framework.exceptions import NotFound  
import requests
from .paypal_api import get_access_token
from .paypal_config import PAYPAL_API_BASE
from rest_framework.generics import RetrieveAPIView
from django.db import transaction
from .models import PasswordResetAttempt, get_end_of_month, update_student_statistics
from accounts.permissions import IsParent, IsAgent



# School Year Views
class SchoolYearList(mixins.ListModelMixin, generics.GenericAPIView):
    queryset = SchoolYear.objects.all()
    serializer_class = SchoolYearSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class LatestSchoolYearView(RetrieveAPIView):
    queryset = SchoolYear.objects.all().order_by('-start_date')
    serializer_class = SchoolYearSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.get_queryset().first()

class PreviousSchoolYearView(RetrieveAPIView):
    queryset = SchoolYear.objects.all().order_by('-start_date')
    serializer_class = SchoolYearSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        queryset = self.get_queryset()
        if queryset.count() < 2:
            raise NotFound("L'avant-dernière année scolaire n'est pas disponible.")
        return queryset[1]

class SchoolListView(generics.ListAPIView):
    queryset = School.objects.all()
    serializer_class = SchoolSerializer

# Authentication Views
# def get_auth_for_user(user):
#     tokens = RefreshToken.for_user(user)
#     return {
#         'user': UserSerializer(user).data,
#         'tokens': {
#             'access': str(tokens.access_token),
#             'refresh': str(tokens),
#         }
#     }    



class UpdateStudentProfilePhoto(generics.UpdateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentPhotoSerializer
    permission_classes = [IsAuthenticated, IsParent]

    def get_object(self):
        student_id = self.kwargs.get('pk')
        return Student.objects.get(pk=student_id)

# Agent Schools views
class AgentSchoolView(generics.ListAPIView):
    serializer_class = SchoolSerializer
    permission_classes = [IsAuthenticated, IsAgent]

    def get_queryset(self):
        # Récupérer l'utilisateur actuel
        agent = self.request.user
        # Filtrer les écoles où l'agent est affecté
        queryset = School.objects.filter(agent=agent)
        return queryset

# Classes views
class ClasseList(generics.ListCreateAPIView):
    queryset = Classe.objects.all()
    serializer_class = ClasseSerializer
    permission_classes = [IsAuthenticated, IsAgent]

    def perform_create(self, serializer):
        agent = self.request.user
        school = School.objects.filter(agent=agent).first()
        school_year_id = self.request.data.get('school_year')

        if not school_year_id:
            raise ValidationError("L'année scolaire est requise.")

        try:
            school_year = SchoolYear.objects.get(id=school_year_id)
        except SchoolYear.DoesNotExist:
            raise ValidationError("L'année scolaire spécifiée n'existe pas.")

        if school and school_year:
            serializer.save(school=school, school_year=school_year)
        else:
            raise ValidationError("L'agent n'est pas affecté à une école ou année scolaire.")

    def get_queryset(self):
        agent = self.request.user
        school = School.objects.filter(agent=agent).first()
        school_year_id = self.request.query_params.get('school_year_id')

        if not school_year_id:
            raise ValidationError("L'année scolaire est requise dans les paramètres de requête.")

        try:
            school_year = SchoolYear.objects.get(id=school_year_id)
        except SchoolYear.DoesNotExist:
            raise ValidationError("L'année scolaire spécifiée n'existe pas.")

        if school and school_year:
            return Classe.objects.filter(school=school, school_year=school_year)
        else:
            return Classe.objects.none()
        
class ClasseDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Classe.objects.all()
    serializer_class = ClasseSerializer
    permission_classes = [IsAuthenticated, IsAgent]

class ClasseByLevelView(generics.ListAPIView):
    serializer_class = ClasseSerializer
    permission_classes = [IsAuthenticated, IsAgent]

    def get_queryset(self):
        agent = self.request.user

        if agent.role != 'agent':
            raise PermissionDenied("Vous devez être un agent pour accéder à cette ressource.")

        school = School.objects.filter(agent=agent).first()

        if not school:
            return Classe.objects.none()

        level = self.request.query_params.get('level')

        latest_school_year = SchoolYear.objects.latest('start_date')

        if level:
            return Classe.objects.filter(school=school, level=level, school_year=latest_school_year)
        else:
            return Classe.objects.filter(school=school, school_year=latest_school_year)

class SchoolClassesList(generics.ListAPIView):
    serializer_class = ClasseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        school_id = self.kwargs.get('school_id')
        
        try:
            school = School.objects.get(id=school_id)
            return Classe.objects.filter(school=school)
        except ObjectDoesNotExist:
            raise ValidationError("L'école spécifiée n'existe pas.")
        
# Students views
class StudentList(generics.ListCreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated, IsAgent]

    def perform_create(self, serializer):
        # Récupérer l'utilisateur actuel (agent)
        agent = self.request.user

        # Récupérer l'école de l'agent
        school = School.objects.filter(agent=agent).first()

        # Récupérer l'année scolaire et la classe
        school_year_id = self.request.data.get('school_year_id')
        classe_id = self.request.data.get('classe_id')
        
        if not school_year_id or not classe_id:
            raise ValidationError("L'année scolaire et la classe sont obligatoires.")

        try:
            school_year = SchoolYear.objects.get(id=school_year_id)
            classe = Classe.objects.get(id=classe_id)
        except SchoolYear.DoesNotExist:
            raise ValidationError("L'année scolaire n'existe pas.")
        except Classe.DoesNotExist:
            raise ValidationError("La classe n'existe pas.")

        # Vérifier si l'agent est affecté à une école et si l'année scolaire et la classe sont définies
        if school and school_year and classe:
            serializer.save(school_year=school_year, classe=classe)
        else:
            raise ValidationError("L'agent n'est pas affecté à une école ou l'année scolaire est manquante.")

    def get_queryset(self):
        # Récupérer l'utilisateur actuel (agent)
        agent = self.request.user

        # Récupérer l'école de l'agent
        school = School.objects.filter(agent=agent).first()
        school_year_id = self.request.query_params.get('school_year_id', None)

        if school and school_year_id:
            try:
                school_year = SchoolYear.objects.get(id=school_year_id)
                # Renvoyer les étudiants de la classe associée à l'école de l'agent et à l'année scolaire
                return Student.objects.filter(classe__school=school, school_year=school_year)
            except SchoolYear.DoesNotExist:
                return Student.objects.none()
        else:
            # Renvoyer une liste vide si l'agent n'est affecté à aucune école
            return Student.objects.none()

class StudentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

class StudentByClassList(generics.ListAPIView):
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated, IsAgent]

    def get_queryset(self):
        agent = self.request.user
        school = School.objects.filter(agent=agent).first()

        if school:
            classe_id = self.kwargs.get('pk')

            if classe_id:
                classe = get_object_or_404(Classe, pk=classe_id, school=school)
                # Filtrer les étudiants par classe et école de l'agent
                return Student.objects.filter(classe=classe)
            else:
                raise ValidationError("L'ID de la classe est requis.")
        else:
            raise ValidationError("L'agent n'est pas affecté à une école.")
        
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        classe_id = self.kwargs.get('pk')

        if classe_id:
            classe = get_object_or_404(Classe, pk=classe_id)
            teacher = Teacher.objects.filter(classe=classe).first() 

            # Serialize the teacher data
            teacher_data = TeacherSerializer(teacher).data if teacher else None

            # Add the teacher information to the response data
            response.data = {
                "students": response.data,
                "classInfo": {
                    "class_id": classe.id,
                    "class_name": classe.name,
                    "teacher": teacher_data,
                }
            }

        return response
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_student_by_matricule(request):
    if request.method == 'POST':
        matricule = request.data.get('matricule')
        try:
            student = Student.objects.get(matricule=matricule)
            serializer = StudentSerializer(student)
            return Response(serializer.data)
        except Student.DoesNotExist:
            return Response({'error': 'Élève non trouvé'}, status=404)

# Teachers views
class TeacherList(generics.ListCreateAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated, IsAgent]

    def perform_create(self, serializer):
        agent = self.request.user
        school = School.objects.filter(agent=agent).first()
        school_year_id = self.request.data.get('school_year_id')
        classe_id = self.request.data.get('classe_id')

        if not school_year_id or not classe_id:
            raise ValidationError("L'année scolaire et la classe sont obligatoires.")

        try:
            school_year = SchoolYear.objects.get(id=school_year_id)
            classe = Classe.objects.get(id=classe_id)
        except SchoolYear.DoesNotExist:
            raise ValidationError("L'année scolaire n'existe pas.")
        except Classe.DoesNotExist:
            raise ValidationError("La classe n'existe pas.")

        if school:
            serializer.save(school_year=school_year, classe=classe)
        else:
            raise ValidationError("L'agent n'est pas affecté à une école ou l'année scolaire est manquante.")

    def get_queryset(self):
        agent = self.request.user
        school = School.objects.filter(agent=agent).first()

        if school:
            return Teacher.objects.filter(classe__school=school)
        else:
            return Teacher.objects.none()

class TeacherDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated, IsAgent]

class TeachersByYearView(generics.ListAPIView):
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated, IsAgent]
    
    def get_queryset(self):
        agent = self.request.user
        school = School.objects.filter(agent=agent).first()
        year_id = self.kwargs['year_id']

        if school:
            return Teacher.objects.filter(classe__school=school, school_year__id=year_id)
        else:
            return Teacher.objects.none()