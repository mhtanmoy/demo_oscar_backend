import django_filters
from django_filters.rest_framework import FilterSet
from utils.product_discount import product_discount

from oscar.apps.catalogue.models import (
    ProductClass,
    ProductAttribute,
    ProductAttributeValue,
)
from oscar.apps.partner.models import StockRecord

from .models import *

class ProductFilter(FilterSet):
    is_stock = django_filters.BooleanFilter(label='is_stock', method='filter_is_stock')
    is_wishlist = django_filters.BooleanFilter(label='is_wishlist', method='filter_is_wishlist')
    discount = django_filters.CharFilter(label='discount', method='filter_discount')
    category = django_filters.CharFilter(label='category', method='filter_category')
    partner_type = django_filters.CharFilter(label='partner_type', method='filter_partner_type')
    ordering = django_filters.CharFilter(label='ordering',method="filter_ordering")
    class Meta:
        model = Product 
        fields = ("id","title", "slug","is_public","is_stock","discount","category","partner_type","is_wishlist","ordering")

    def filter_ordering(self, objects, name, value):
        objects_filtered=[]
        for obj in objects:
            objects_filtered.append(obj.pk)
        if value in ['id','-id','title','-title','slug','-slug','price','-price']:
            if value in ['price']:
                queryset = Product.objects.filter(pk__in=objects_filtered).order_by("stockrecords__price")
            elif value in ['-price']:
                queryset = Product.objects.filter(pk__in=objects_filtered).order_by("-stockrecords__price")
            else:
                queryset = Product.objects.filter(pk__in=objects_filtered).order_by(value)
        else:
            queryset = Product.objects.filter(pk__in=objects_filtered)

        return queryset

    def filter_partner_type(self, objects, name, value):
        # objects_partner_type=[]
        # for obj in objects:
        #     qs = obj.categories.all().last()
        #     if qs:
        #         if qs.partner_type:
        #             if qs.partner_type.name==value:
        #                 objects_partner_type.append(obj.pk)

        if value:
            queryset = Product.objects.filter(categories__partner_type__name__icontains=value)
        else:
            queryset = Product.objects.none()

        return queryset
            
    def filter_category(self, objects, name, value):
        objects_category=[]
        for obj in objects:
            qs = obj.categories.all().last()
            if qs:
                if qs.name==value:
                    objects_category.append(obj.pk)

        if objects_category:
            queryset = Product.objects.filter(pk__in=objects_category)
        else:
            queryset = Product.objects.none()

        return queryset


    def filter_discount(self, objects, name, value):
        if value:
            queryset = Product.objects.filter(discount__title__icontains=value)
        else:
            queryset = Product.objects.none()

        return queryset

    def filter_is_stock(self, objects, name, value):
        objects_true=[]
        objects_false=[]
        for obj in objects:
            if obj.has_stockrecords:
                if obj.stockrecords.first().num_in_stock >= 0:
                    objects_true.append(obj.pk)
            else:
                objects_false.append(obj.pk)
                    
        if value==True:
            queryset = Product.objects.filter(pk__in=objects_true)
        elif value==False:
            queryset = Product.objects.filter(pk__in=objects_false)
        else:
            queryset = Product.objects.none()

        return queryset

    def filter_is_wishlist(self, objects, name, value):
        objects_true=[]
        objects_false=[]
        for obj in objects:
            user = self.request.user

            if user:
                if user.is_authenticated:
                    if obj.wishlists_lines.filter(wishlist__owner__id=user.id).exists():
                        objects_true.append(obj.pk)
                    else:
                        objects_false.append(obj.pk)
                    
        if value==True:
            queryset = Product.objects.filter(pk__in=objects_true)
        elif value==False:
            queryset = Product.objects.filter(pk__in=objects_false)
        else:
            queryset = Product.objects.none()

        return queryset
    

class CategoryFilter(FilterSet):
    class Meta:
        model = Category 
        fields = ("name", "slug")

class PromoCodeFilter(FilterSet):
    class Meta:
        model = PromoCode 
        fields = ("code",)

class DiscountFilter(FilterSet):
    class Meta:
        model = Discount 
        fields = ("title",)

class ProductClassFilter(FilterSet):
    class Meta:
        model = ProductClass 
        fields = ("name", "slug")

class ProductAttributeFilter(FilterSet):
    class Meta:
        model = ProductAttribute 
        fields = ("name", "code")

class ProductAttributeValueFilter(FilterSet):
    class Meta:
        model = ProductAttributeValue 
        fields = ("product__id",)

class StockRecordFilter(FilterSet):
    class Meta:
        model = StockRecord 
        fields = ("product__id",)