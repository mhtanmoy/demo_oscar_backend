from .models import *
import django_filters

class ZoneFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model = Zone 
        fields = ("title", "is_active")

class SubZoneFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model = SubZone 
        fields = ("name", "is_active","zone")

class PartnerTypeFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model = PartnerType 
        fields = ("name", "slug",)

class PartnerFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model = Partner 
        fields = ("grade", "partner_type","name")