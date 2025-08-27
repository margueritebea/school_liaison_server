from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [

    # Categorie Notifications
    path('category-notifications/', views.CategorieNotificationView.as_view(), name='categorie_notification'),
    
    # Agent Notifications
    path('agents/send-notifications/', views.NotificationCreateView.as_view(), name='send_notifications'),
    path('agents/students/notifications-by-class/', views.AgentStudentsNotificationsByClassList.as_view(), name='sent_notifications_by_class'),
    path('agents/notifications/students/', views.AgentNotificationsByStudent.as_view(), name='agent-notifications-by-student'),
    
    # Parent Student Notifications
    path('parents/notifications/student/<int:student_id>/', views.ParentNotificationsByStudent.as_view(), name='parent-notifications-by-student'),
    path('parents/notifications/<int:user_notification_id>/', views.ParentNotificationDetail.as_view(), name='parent_student_notifications_list'),
    path('parents/notifications/unread-count/', views.UnreadNotificationCountView.as_view(), name='unread-notifications-count'),
    path('parents/notifications/unread-by-student/', views.UnreadNotificationsByStudentView.as_view(), name='unread-notifications-by-student'),

]
