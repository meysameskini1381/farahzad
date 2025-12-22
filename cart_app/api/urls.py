from .views import *
from django.urls import path


urlpatterns = [
    path("add/", AddToCartAPIView.as_view(), name="cart-add"),
    path("get/", GetCartAPIView.as_view(), name="cart-get"),
    path("update/<int:item_id>/", UpdateCartItemAPIView.as_view(), name="cart-update"),
    path("delete/<int:item_id>/", DeleteCartItemAPIView.as_view(), name="cart-delete"),
]
