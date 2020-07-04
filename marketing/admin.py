from django.contrib import admin
from django.utils.html import format_html
from .models import *
# Register your models here.
admin.site.register(City)


class BannerAdmin(admin.ModelAdmin):
    fields = ('title', 'image_tag',  'image')
    readonly_fields = ('image_tag',)

    def image_tag(self, obj):
        return format_html('<img width="300" height="150" src="{}" />'.format(obj.image.url))

    image_tag.short_description = 'Image'


admin.site.register(Banner, BannerAdmin)
