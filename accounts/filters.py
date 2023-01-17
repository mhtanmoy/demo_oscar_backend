import django_filters
from django_filters.rest_framework import FilterSet
from .models import *

class EmployeeFilter(FilterSet):
    class Meta:
        model = Employee
        fields = ("id", "status")