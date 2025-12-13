from django.contrib import admin
from django.urls import path
from .models import *
from .views import HomeView

app_name = 'home_app'

urlpatterns = [

    path('',HomeView.as_view(),name='home'),

]