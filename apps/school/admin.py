from django.contrib import admin

from .models import Classe, School, Student, Teacher, SchoolYear, StudentStatistics

@admin.register(SchoolYear)
class SchoolYearAdmin(admin.ModelAdmin):
    list_display = ['id', 'start_date', 'end_date']


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'address',  'agent']


@admin.register(Classe)
class ClasseAdmin(admin.ModelAdmin):
    list_display = ['id', 'school', 'name',  'level']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['id', 'matricule', 'first_name', 'last_name',  'classe', 'date_of_birth']


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name',  'classe', 'phone', 'school_year']

@admin.register(StudentStatistics)
class StudentStatisticsAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'student', 'school_year', 
        'absence', 'absence_autorisee', 'presence', 'mauvaise_conduite', 'bonne_conduite', 
        'participation_faible', 'participation_moyenne', 'participation_active', 'mauvaise_moyenne', 'bonne_moyenne'
    ]
