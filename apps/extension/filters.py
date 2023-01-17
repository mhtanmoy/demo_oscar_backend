from oscarapi.serializers.checkout import Country
from apps.catalogue.models import Product,Category
from apps.partner.models import Partner
import django_filters

class HomePageFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model = Product
        fields = ("id","upc","title","rating","categories")


class PartnerFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model = Partner
        fields = ("id","partner_type","grade","zone","name")

class CustomProductFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model = Product
        fields = ("id","slug","title","rating")
        extra_fields = ["price"]

class CustomCategoryFilter(django_filters.rest_framework.FilterSet):
    partner_type = django_filters.CharFilter(label='partner_type', method='filter_partner_type')

    class Meta:
        model = Category
        fields = ("id", "name", "slug", "partner_type")

    def filter_partner_type(self, objects, name, value):
        # objects_partner_type=[]
        # for obj in objects:
        #     if obj.partner_type:
        #         if obj.partner_type.name == value:
        #             objects_partner_type.append(obj.pk)

        if value:
            queryset =Category.objects.filter(partner_type__name__icontains=value)
        else:
            queryset = Category.objects.none()

        return queryset

class CustomChildCategoryFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model = Category
        fields = ("id", "name", "slug", "partner_type")
        extra_fields = ["parent_category"]

class CustomCountryFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model = Country
        depth = 1
        fields = ("printable_name", "name", "iso_3166_1_a2", "iso_3166_1_numeric", "is_shipping_country")