from django.contrib import admin
from .models import *
from .models import Discount, PromoCode

class DiscountAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'schedule_type', 'discount_type']

    class Meta:
        model = Discount


admin.site.register(Discount, DiscountAdmin)


class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'promo_type']

    class Meta:
        model = PromoCode


admin.site.register(PromoCode, PromoCodeAdmin)

from oscar.apps.catalogue.admin import *  # noqa
