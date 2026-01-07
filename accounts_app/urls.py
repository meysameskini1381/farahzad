from django.urls import path, include
from accounts_app.views import *


app_name = 'accounts_app'

urlpatterns = [
    path('about-us/', about_us_view, name='about_us'),
]
