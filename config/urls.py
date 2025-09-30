from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('gotoadminsite/', admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/school/", include("school.urls")),
    path("api/notifications/", include("notification.urls")),
    path("api/payment/", include("payment.urls")),
]
