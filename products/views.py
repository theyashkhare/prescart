from rest_framework import viewsets
from rest_framework import generics

from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter, OrderingFilter
from .pagination import ProductPagination, CategoryPagination
from .serializers import *
from .models import *


class ProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        SearchFilter,
    ]
    search_fields = ["title", "description",
                     'categories__title', 'categories__id', 'categories__slug']
    pagination_class = ProductPagination


class ProductRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer


class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    pagination_class = CategoryPagination
    serializer_class = CategorySerializer


class CategoryRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryDetailSerializer
