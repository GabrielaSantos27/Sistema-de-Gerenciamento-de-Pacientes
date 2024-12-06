from django.urls import path
from core.views import Home_view

urlpatterns = [
    path("", Home_view.home_view, name='home')
]