from django.contrib.messages import api
from django.urls import path,include
from .views import *

app_name = "products_app"

urlpatterns = [
    path(
        "products-category/<slug:category_slug>/",
        product_by_category,
        name="product_by_category",
    ),
    path('product-detail/<slug:product_slug>/', product_detail, name='product_detail'),
    path("api/", include("products_app.api.urls")),
]
