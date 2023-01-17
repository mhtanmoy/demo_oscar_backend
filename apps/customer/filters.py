import django_filters
from django_filters.rest_framework import FilterSet
from oscar.core.loading import get_model

Order = get_model('order', 'Order')

class OrderFilter(FilterSet):
    class Meta:
        model = Order 
        fields = ("user__username", "number")