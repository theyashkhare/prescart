from rest_framework import serializers
from .models import *


class BannerSerializer(serializers.HyperlinkedModelSerializer):
    image = serializers.SerializerMethodField("get_image")

    class Meta:
        model = Banner
        fields = '__all__'

    def get_image(self, obj):
        try:
            return obj.image.url
        except:
            return None


class CitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = City
        fields = ['name', 'zipcodes', ]
