from django.urls import path

from .views import EdeshViewSet

urlpatterns = [
    path(
        "delivery/shipment/",
        EdeshViewSet.as_view({"post": "create_shipment"}),
        name="create-shipment",
    ),
    path(
        "delivery/label/",
        EdeshViewSet.as_view({"post": "label_print"}),
        name="label-print",
    ),
    path(
        "delivery/track/",
        EdeshViewSet.as_view({"post": "tract_parcel"}),
        name="tract-parcel",
    ),
    path(
        "delivery/coverage/area/",
        EdeshViewSet.as_view({"get": "coverage_area"}),
        name="coverage-area",
    ),
]
