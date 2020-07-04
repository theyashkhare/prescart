from django.urls import include, path
from django.conf.urls import url
from .views import *


api_urlpatterns = [
    path('', ProductListAPIView.as_view(), name='api_products'),
    path('<int:pk>/', ProductRetrieveAPIView.as_view(), name='product-detail'),
    path('categories/', CategoryListAPIView.as_view(), name='api_categories'),
    path('categories/<int:pk>/', CategoryRetrieveAPIView.as_view(),
         name='category-detail'),
]

urlpatterns = [
]
