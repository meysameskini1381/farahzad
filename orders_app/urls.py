from django.urls import path
from .views import order_detail

app_name = 'orders'

urlpatterns = [
    path('<int:order_id>/', order_detail, name='order-detail'),
]