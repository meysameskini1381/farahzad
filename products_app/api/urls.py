from django.urls import path
from .views import *

urlpatterns = [
    path("products/", ProductListAPIView.as_view(),name="api_products_by_category"),
    path('product_category/', ProductCategoryAPIView.as_view(), name='api-products-by-category'),
    path('product-detail/<slug:slug>/', ProductDetailAPIView.as_view()),
    path('product/<slug:slug>/comment/', ProductCommentBySlugAPIView.as_view(), name='product-comment'),

]