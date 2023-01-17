
from django.contrib import admin
from .models import *
from django.contrib.gis.admin import OSMGeoAdmin


class PartnerTypeAdmin(admin.ModelAdmin):
    list_display = ['name']
    class Meta:
        model = PartnerType
    # exclude = ['slug']


admin.site.register(PartnerType, PartnerTypeAdmin)


# admin.site.register(Partner)

admin.site.register(SubZone)

@admin.register(Zone)
class ShopAdmin(OSMGeoAdmin):
    list_display = ('title', 'location')

from oscar.apps.partner.admin import *  # noqa
