from django.urls import path
from ..views import profile_view
from .views import (
    ProfileView,
    AddressListCreateView,
    AddressDetailView
)

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('addresses/', AddressListCreateView.as_view(), name='address-list'),
    path('addresses/<int:pk>/', AddressDetailView.as_view(), name='address-detail'),
    path('profile-user',profile_view,name='profile-user'),
]