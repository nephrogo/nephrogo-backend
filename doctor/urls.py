from django.urls import path

from doctor import views

app_name = 'doctor'

urlpatterns = [
    path('', views.SummaryView.as_view(), name="index"),
    path('nutrition/', views.NutritionView.as_view(), name="nutrition"),
    path('health/', views.HealthStatusView.as_view(), name="health_status"),
]
