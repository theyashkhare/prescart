from rest_framework import serializers

from .models import *


class VariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variation
        fields = [
            "id",
            "title",
            "price", "sale_price", "tax","kind",
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    variation_set = VariationSerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "description",
            "price",
            "tax",
            "image",
            "variation_set",
        ]

    def get_image(self, obj):
        return obj.productimage_set.first().image.url


class ProductSerializer(serializers.ModelSerializer):
    variation_set = VariationSerializer(many=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "description", "tax", "price",
            "image",
            "variation_set",
        ]

    def get_image(self, obj):
        try:
            return obj.productimage_set.first().image.url
        except:
            return None


class CategoryDetailSerializer(serializers.ModelSerializer):
    product_set = ProductSerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "url",
            "id",
            "image",
            "title",
            "description",
            "product_set",
        ]

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        else:
            return None


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id",
            "image",
            "title",
            "slug",
        ]

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        else:
            return None
