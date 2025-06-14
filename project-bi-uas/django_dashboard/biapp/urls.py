from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_utama, name='dashboard_utama'),
]