from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet
from orders_app.views import *
router = DefaultRouter()
router.register('', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
    path('test/',order_user,name='test'),
]