from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

app_label = 'marketing'
router = DefaultRouter()

router.register('banners', BannerViewSet)
router.register('cities', CityViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
