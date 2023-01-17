from oscar.core.loading import get_model
from rest_framework.permissions import IsAuthenticated

from utils.custom_viewset import CustomViewSet
from .serializers import OrderHistorySerializer
from apps.order.serializers import OrderDetailsSerializer
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from .filters import *

Order = get_model('order', 'Order')

class OrderHistoryViewSet(CustomViewSet):
    serializer_class = OrderDetailsSerializer
    queryset = Order.objects.all()
    lookup_field = "pk"
    # permission_classes = IsAuthenticated
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_fields = ("user__username", "number")
    filterset_class = OrderFilter

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        page_qs = self.paginate_queryset(qs)
        serializer = CustomProductListSerializer(instance=page_qs, many=True, context={"request": request})
        paginated_data = self.get_paginated_response(serializer.data)
        return ResponseWrapper(data = paginated_data.data, msg='Success')