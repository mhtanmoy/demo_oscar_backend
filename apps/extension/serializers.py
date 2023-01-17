from asyncore import read
from dataclasses import field, fields
from .models import *
from rest_framework import serializers
from oscarapi.serializers.checkout import Country

from apps.catalogue.models import Category, Product
from apps.order.models import Order
from apps.partner.models import PartnerType
from utils.product_discount import product_discount
from drf_extra_fields.fields import Base64FileField, Base64ImageField
# ..........***.......... Category ..........***..........
class CustomCategoryListSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    partner_type = serializers.SerializerMethodField(read_only=True)
    discount = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ("id", "name", "slug", "image","children", "partner_type", "discount")
    
    def get_discount(self, obj):
        return product_discount(obj)

    def get_children(self, obj):
        data = obj.get_descendants_and_self().exclude(name__iexact=obj.name)
        child = []
        if data:
            for d in data:
                c = {
                    "id": d.id,
                    "name": d.name,
                    "slug":d.slug
                }
                child.append(c)
        return child

    def get_partner_type(self, obj):
        if obj.partner_type:
            return {
                "id": obj.partner_type.id,
                "name": obj.partner_type.name,
            }
        return None


class SubCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = "__all__"



class CustomCategorySerializer(serializers.ModelSerializer):
    path = serializers.CharField(read_only=True)
    meta_title = serializers.CharField(read_only=True)
    meta_description = serializers.CharField(read_only=True)
    slug = serializers.CharField(read_only=True)
    children = serializers.SerializerMethodField()
    partner_type = serializers.PrimaryKeyRelatedField(
        read_only=False, queryset=PartnerType.objects.all()
    )
    depth = serializers.IntegerField(default=1,initial=1,required=False)
    partner_type_detail = serializers.SerializerMethodField(read_only=True)
    parent_category = serializers.IntegerField(required=False)
    image = Base64ImageField()
    thumbnail_image = Base64ImageField()

    class Meta:
        model = Category
        fields = "__all__"
        extra_fields = ["parent_category"]

    def get_children(self, obj):
        data = obj.get_descendants_and_self().exclude(name__iexact=obj.name)
        serializer = SubCategorySerializer(data=data, many=True)
        serializer.is_valid()
        return serializer.data

    def get_partner_type_detail(self, obj):
        if obj.partner_type:
            return {
                "id": obj.partner_type.id,
                "name": obj.partner_type.name,
                "slug": obj.partner_type.slug,
            }
        return obj.partner_type

    def create(self, validated_data):
        image = validated_data.pop('image', None)
        thumbnail_image = validated_data.pop('thumbnail_image', None)
        if image and thumbnail_image:
            return Category.objects.create(image=image,thumbnail_image=thumbnail_image, **validated_data)           
        elif image: 
            return Category.objects.create(image=image, **validated_data)
        # elif thumbnail_image:
        #     return Category.objects.create(thumbnail_image=thumbnail_image, **validated_data)
        return Category.objects.create(**validated_data)

class CustomChildCategorySerializer(serializers.ModelSerializer):
    path = serializers.CharField(read_only=True)
    meta_title = serializers.CharField(read_only=True)
    meta_description = serializers.CharField(read_only=True)
    slug = serializers.CharField(read_only=True)
    children = serializers.SerializerMethodField()
    partner_type = serializers.PrimaryKeyRelatedField(
        read_only=False, queryset=PartnerType.objects.all()
    )
    partner_type_detail = serializers.SerializerMethodField(read_only=True)
    parent_category = serializers.IntegerField(write_only=True)
    parent_category_details = serializers.SerializerMethodField()
    depth = serializers.IntegerField(required=False)
    image = Base64ImageField()
    thumbnail_image = Base64ImageField()

    class Meta:
        model = Category
        fields = "__all__"
        extra_fields = ["parent_category"]

    def get_children(self, obj):
        try:
            data = obj.get_descendants_and_self().exclude(name__iexact=obj.name)
            serializer = SubCategorySerializer(data=data, many=True)
            if serializer.is_valid():
                return serializer.data
        except:
            return []

    def get_partner_type_detail(self, obj):
        try:
            if obj.partner_type:
                return {
                    "id": obj.partner_type.id,
                    "name": obj.partner_type.name,
                    "slug": obj.partner_type.slug,
                }
            return obj.partner_type
        except:
            return []

    def get_parent_category_details(self, obj):
        try:
            data = obj.get_root()
            return {"id": data.id, "name": data.name}
        except:
            return {}

    def create(self, validated_data):
        image = validated_data.pop('image', None)
        thumbnail_image = validated_data.pop('thumbnail_image', None)
        if image and thumbnail_image:
            return Category.objects.create(image=image,thumbnail_image=thumbnail_image, **validated_data)           
        elif image: 
            return Category.objects.create(image=image, **validated_data)
        # elif thumbnail_image:
        #     return Category.objects.create(thumbnail_image=thumbnail_image, **validated_data)
        return Category.objects.create(**validated_data)


class ZoneWizeProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        depth = 1
        fields = "__all__"


class CustomCountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        depth = 1
        fields = "__all__"


class HomePageDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        depth = 1
        fields = "__all__"
