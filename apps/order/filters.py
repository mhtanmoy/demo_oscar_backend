
from .models import *
from django_filters.rest_framework import FilterSet

class OrderDetailsFilter(FilterSet):
    class Meta:
        model = Order
        fields = ("status","zone")


class ScheduleFilter(FilterSet):
    class Meta:
        model = Schedule
        fields = ("is_active",)

class OrderCountPerScheduleFilter(FilterSet):
    class Meta:
        model = OrderCountPerSchedule
        fields = ("is_active",)