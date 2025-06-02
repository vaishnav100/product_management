from django.urls import path, include
from .views import ProductAPIView, ProductListAPIView, ProductUpdateAPIView


urlpatterns = [
    path('', ProductAPIView.as_view(), name='product_create'),
    path('list/', ProductListAPIView.as_view(), name='product_list'),
    path('update/<int:pk>/', ProductUpdateAPIView.as_view(), name='product_update'),
    path('delete/<int:pk>/', ProductUpdateAPIView.as_view(), name='product_delete'),
]