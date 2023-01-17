from .models import *
import django_filters
from apps.catalogue.models import Product
class LineFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model = Line 
        fields = ("wishlist", "title")

class WishListFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model = Product 
        fields = ("categories", "is_public")