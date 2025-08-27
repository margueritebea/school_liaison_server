from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('gotoadminsite/', admin.site.urls),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/school/", include("apps.school.urls")),
    path("api/notifications/", include("apps.notification.urls")),
    path("api/payment/", include("apps.payment.urls")),
]
