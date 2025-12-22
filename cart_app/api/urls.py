from .views import *
from django.urls import path


urlpatterns = [
    path("add/", AddToCartAPIView.as_view(), name="cart-add"),
]
