from django.urls import path

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from . import views

urlpatterns = [
    # Authentication
    path('signin/', views.SignInView.as_view(), name='signin'),
    path('token/refresh/', TokenRefreshView.as_view(), name='refresh_token'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('send-reset-code/email/', views.SendResetCodeByEmailView.as_view(), name='send_reset_code_by_email'),
    path('confirm-reset-password/email/', views.ConfirmResetCodeByEmailView.as_view(), name='confirm_reset_password_by_email'),
    path('reset-password/email/', views.ResetPasswordByEmailView.as_view(), name='reset_password_by_email'),
    path('delete-account/', views.DeleteAccountView.as_view(), name='delete-account'),

    # # Profile
    path('profil/', views.ProfileList.as_view(), name='profil'),
    path('profil/<int:pk>/', views.ProfileDetail.as_view(), name='profil_detail'),
    path('profile/photo/', views.ProfilePhotoView.as_view(), name='profile-photo'),
    # path('profile/<int:profile_id>/student-list/', views.ProfileStudentView.as_view(), name='profile_student_list'),
    # path('profile/<int:profile_id>/profil-add-student/', views.ProfileAddStudent.as_view(), name='profile_add_student'),
    # path('profile/<int:profile_id>/remove-student/<int:student_id>/', views.RemoveStudentFromProfileView.as_view(), name='remove-student-from-profile'),

]
