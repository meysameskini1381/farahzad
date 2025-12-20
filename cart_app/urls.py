from django.urls import path,include


cart_app = 'cart_app'

urlpatterns = [
    path("api/cart/", include("cart_app.api.urls")),
    ]



