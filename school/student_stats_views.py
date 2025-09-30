from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Avg, FloatField
from django.db.models.functions import Coalesce

from .models import Student, Classe, School, StudentStatistics, SchoolYear
from .student_stats_serializers import (
    StudentPerformanceSerializer,
    SchoolClassPerformanceSerializer,
    SchoolLevelPerformanceSerializer,
    SchoolPerformanceSerializer
)


class BasePerformanceView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_school_year(self):
        return SchoolYear.objects.latest('start_date')
    
    def get_date_range(self, request):
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        
        if month and year:
            first_day = datetime(int(year), int(month), 1).date()
            last_day = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            return first_day, last_day
        return None, None


class StudentPerformanceView(BasePerformanceView):
    def get(self, request, student_id):
        student = get_object_or_404(Student, pk=student_id)
        school_year = self.get_school_year()
        
        statistics = StudentStatistics.objects.filter(
            student=student,
            school_year=school_year
        ).first()
        
        if not statistics:
            statistics = StudentStatistics(student=student, school_year=school_year)
            statistics.save()
        
        serializer = StudentPerformanceSerializer(student, context={
            'school_year': school_year,
            'request': request
        })
        return Response(serializer.data)


class SchoolClassPerformanceView(BasePerformanceView):
    def get(self, request, school_id, class_id):
        school = get_object_or_404(School, pk=school_id)
        classe = get_object_or_404(Classe, pk=class_id, school=school)
        school_year = self.get_school_year()
        start_date, end_date = self.get_date_range(request)
        
        students = Student.objects.filter(classe=classe, school_year=school_year)
        stats = self.calculate_stats(students, school_year, start_date, end_date)
        
        serializer = SchoolClassPerformanceSerializer({
            'school': school,
            'classe': classe,
            'stats': stats,
            'school_year': school_year
        })
        return Response(serializer.data)
    
    def calculate_stats(self, students, school_year, start_date=None, end_date=None):
        filter_kwargs = {
            'student__in': students,
            'school_year': school_year
        }
        
        if start_date and end_date:
            filter_kwargs['notification__date__range'] = [start_date, end_date]
        
        return StudentStatistics.objects.filter(**filter_kwargs).aggregate(
            total_students=Count('student', distinct=True),
            total_absence=Coalesce(Sum('absence'), 0),
            total_absence_autorisee=Coalesce(Sum('absence_autorisee'), 0),
            total_presence=Coalesce(Sum('presence'), 0),
            total_mauvaise_conduite=Coalesce(Sum('mauvaise_conduite'), 0),
            total_bonne_conduite=Coalesce(Sum('bonne_conduite'), 0),
            total_participation_active=Coalesce(Sum('participation_active'), 0),
            total_participation_moyenne=Coalesce(Sum('participation_moyenne'), 0),
            total_participation_faible=Coalesce(Sum('participation_faible'), 0),
            total_bonne_moyenne=Coalesce(Sum('bonne_moyenne'), 0),
            total_mauvaise_moyenne=Coalesce(Sum('mauvaise_moyenne'), 0)
        )
    

class SchoolLevelPerformanceView(BasePerformanceView):
    def get(self, request, school_id, level):
        school = get_object_or_404(School, pk=school_id)
        school_year = self.get_school_year()
        start_date, end_date = self.get_date_range(request)
        
        classes = Classe.objects.filter(
            school=school,
            level=level,
            school_year=school_year
        )
        students = Student.objects.filter(classe__in=classes, school_year=school_year)
        stats = self.calculate_stats(students, school_year, start_date, end_date)
        
        serializer = SchoolLevelPerformanceSerializer({
            'school': school,
            'level': level,
            'stats': stats,
            'school_year': school_year,
            'class_count': classes.count(),
            'student_count': students.count()
        })
        return Response(serializer.data)
    
    def calculate_stats(self, students, school_year, start_date=None, end_date=None):
        filter_kwargs = {
            'student__in': students,
            'school_year': school_year
        }
        
        if start_date and end_date:
            filter_kwargs['notification__date__range'] = [start_date, end_date]
        
        return StudentStatistics.objects.filter(**filter_kwargs).aggregate(
            total_absence=Coalesce(Sum('absence'), 0),
            total_absence_autorisee=Coalesce(Sum('absence_autorisee'), 0),
            total_presence=Coalesce(Sum('presence'), 0),
            total_mauvaise_conduite=Coalesce(Sum('mauvaise_conduite'), 0),
            total_bonne_conduite=Coalesce(Sum('bonne_conduite'), 0),
            total_participation_active=Coalesce(Sum('participation_active'), 0),
            total_participation_moyenne=Coalesce(Sum('participation_moyenne'), 0),
            total_participation_faible=Coalesce(Sum('participation_faible'), 0),
            total_bonne_moyenne=Coalesce(Sum('bonne_moyenne'), 0),
            total_mauvaise_moyenne=Coalesce(Sum('mauvaise_moyenne'), 0)
        )


class SchoolPerformanceView(BasePerformanceView):
    def get(self, request, school_id):
        school = get_object_or_404(School, pk=school_id)
        school_year = self.get_school_year()
        start_date, end_date = self.get_date_range(request)
        
        classes = Classe.objects.filter(school=school, school_year=school_year)
        students = Student.objects.filter(classe__in=classes, school_year=school_year)
        stats = self.calculate_stats(students, school_year, start_date, end_date)
        
        serializer = SchoolPerformanceSerializer({
            'school': school,
            'stats': stats,
            'school_year': school_year,
            'class_count': classes.count(),
            'student_count': students.count()
        })
        return Response(serializer.data)
    
    def calculate_stats(self, students, school_year, start_date=None, end_date=None):
        filter_kwargs = {
            'student__in': students,
            'school_year': school_year
        }
        
        if start_date and end_date:
            filter_kwargs['notification__date__range'] = [start_date, end_date]
        
        return StudentStatistics.objects.filter(**filter_kwargs).aggregate(
            total_absence=Coalesce(Sum('absence'), 0),
            total_absence_autorisee=Coalesce(Sum('absence_autorisee'), 0),
            total_presence=Coalesce(Sum('presence'), 0),
            total_mauvaise_conduite=Coalesce(Sum('mauvaise_conduite'), 0),
            total_bonne_conduite=Coalesce(Sum('bonne_conduite'), 0),
            total_participation_active=Coalesce(Sum('participation_active'), 0),
            total_participation_moyenne=Coalesce(Sum('participation_moyenne'), 0),
            total_participation_faible=Coalesce(Sum('participation_faible'), 0),
            total_bonne_moyenne=Coalesce(Sum('bonne_moyenne'), 0),
            total_mauvaise_moyenne=Coalesce(Sum('mauvaise_moyenne'), 0)
        )
    
