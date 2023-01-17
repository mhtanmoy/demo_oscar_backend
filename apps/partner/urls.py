from django.urls import path
from .views import ZoneViewSet, SubZoneViewSet, PartnerViewSet, PartnerTypeViewSet

app_name = "partner"
urlpatterns = [
    path('zone/', ZoneViewSet.as_view(
        {"get": "list", 'post': 'create'}),
         name="zone"),
    path('zone/<pk>/', ZoneViewSet.as_view(
        {"patch": "update", 'delete': 'destroy', 'get': 'retrieve'}),
         name="zone"),

    path('subzone/', SubZoneViewSet.as_view(
        {"get": "list", 'post': 'create'}),
         name="subzone"),

    path('subzone/<pk>/', SubZoneViewSet.as_view(
        {"patch": "update", 'delete': 'destroy', 'get': 'retrieve'}),
         name="subzone"),

    path('partner/', PartnerViewSet.as_view(
        {"get": "list", 'post': 'create'}),
         name="partner"),

    path('partner/<pk>/', PartnerViewSet.as_view(
        {"patch": "update", 'delete': 'destroy', 'get': 'retrieve'}),
         name="partner"),

    path('partner_type/', PartnerTypeViewSet.as_view(
        {"get": "list",'post': 'create'}),
         name="partner_type"),

    path('partner_type/<pk>/', PartnerTypeViewSet.as_view(
        {"patch": "update", 'delete': 'destroy', 'get': 'retrieve'}),
         name="partner"),

    path('approved_partners/', PartnerViewSet.as_view(
        {'get': 'approved_partners'}),
         name="approved_partners"),
]
