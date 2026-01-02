from django.urls import path
from ..views import profile_view
from accounts_app.api.views import *

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('addresses/', AddressListCreateView.as_view(), name='address-list'),
    path('addresses/<int:pk>/', AddressDetailView.as_view(), name='address-detail'),
    path('profile-user',profile_view,name='profile-user'),
    path('auth/send-otp/', SendOTPAPIView.as_view(), name='send_otp'),
    path('auth/verify-otp/', VerifyOTPAPIView.as_view(), name='verify_otp'),
    path('login-register/', auth_page, name='auth_page'),

]