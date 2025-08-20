from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # School Year
    path('schoolyears/', views.SchoolYearList.as_view(), name='schoolyear-list'),
    path('schoolyears/latest/', views.LatestSchoolYearView.as_view(), name='latest-schoolyear'),
    path('schoolyears/previous/', views.PreviousSchoolYearView.as_view(), name='previous-schoolyear'),

    # School 
    path('school/', views.AgentSchoolView.as_view(), name='agent_school'),
    path('schools/', views.SchoolListView.as_view(), name='school-list'),

    # Classe
    path('classe/', views.ClasseList.as_view(), name='classe'),
    path('classe/<int:pk>/', views.ClasseDetail.as_view(), name='classe_detail'),
    path('classes-by-level/', views.ClasseByLevelView.as_view(), name='classes-by-level'),
    path('schools/<int:school_id>/classes/', views.SchoolClassesList.as_view(), name='school-classes-list'),

    # Student
    path('student/', views.StudentList.as_view(), name='student'),
    path('student/<int:pk>/', views.StudentDetail.as_view(), name='student_detail'),
    path('students-by-class/<int:pk>/', views.StudentByClassList.as_view(), name='students_by_class'),
    path('get-student-by-matricule/', views.get_student_by_matricule, name='get_student_id_by_matricule'),
    path('student/<int:pk>/update-photo/', views.UpdateStudentProfilePhoto.as_view(), name='update_student_photo'),

    # Teacher
    path('teacher/', views.TeacherList.as_view(), name='teacher'),
    path('teacher/<int:pk>/', views.TeacherDetail.as_view(), name='teacher_detail'),
    path('teachers-by-year/<int:year_id>/', views.TeachersByYearView.as_view(), name='teachers-by-year'),

]
