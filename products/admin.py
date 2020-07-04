from django.contrib import admin

from .models import Product, Variation, ProductImage, Category, ProductFeatured, Transfer, Vendor


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0
    max_num = 10
    readonly_fields = ('image_preview',)


class VariationInline(admin.TabularInline):
    model = Variation
    extra = 0
    max_num = 10


class ProductAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'price']
    inlines = [
        ProductImageInline,
        VariationInline,
    ]

    class Meta:
        model = Product


# ADDED FIELDS
admin.site.register(Product, ProductAdmin)
admin.site.register(Transfer)
admin.site.register(Vendor)
admin.site.register(Variation)
admin.site.register(ProductImage)
admin.site.register(Category)
admin.site.register(ProductFeatured)
