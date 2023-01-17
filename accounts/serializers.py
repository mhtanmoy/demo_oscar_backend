from django.utils.translation import gettext_lazy as _
from oscar.apps.address.models import UserAddress
from oscar_accounts import models
from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.partner.models import Zone, Partner
from apps.partner.serializers import ZoneSerializer
from django.contrib.auth.models import Permission

from .models import EmployeeCategory, Employee
#from authentications.serializers import UserSerializerCustom
from drf_extra_fields.fields import Base64FileField, Base64ImageField
User = get_user_model()


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Account
        fields = "__all__"


class EmployeeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeCategory
        fields = "__all__"


class EmployeeSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6, write_only=True, required=True)
    last_name = serializers.CharField(max_length=50, required=True)
    user = serializers.CharField(read_only=True)
    # user = serializers.PrimaryKeyRelatedField(
    #                     read_only=False,
    #                     required=False,
    #                     queryset=User.objects.all())
    employee_category = serializers.PrimaryKeyRelatedField(
        read_only=False, required=True, queryset=EmployeeCategory.objects.all()
    )
    image = Base64ImageField(required=False)

    class Meta:
        model = Employee
        depth = 1
        fields = "__all__"
        extra_fields = ("password", "user", "employee_category", "image")

    def to_representation(self, instance):
        self.fields["employee_category"] = EmployeeCategorySerializer(read_only=True)
        return super(EmployeeSerializer, self).to_representation(instance)


class MerchantSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6, write_only=True, required=True)
    employee_category = EmployeeCategorySerializer(read_only=True)
    zone = serializers.IntegerField()
    store_name = serializers.CharField(max_length=50)

    class Meta:
        model = Employee
        fields = (
            "id",
            "first_name",
            "last_name",
            "nid",
            "phone",
            "email",
            "employee_category",
            "is_active",
            "shift_start_hour",
            "shift_end_hour",
            "date_of_birth",
            "image",
            "created_at",
            "updated_at",
            "zone",
            "password",
            "store_name",
        )

        read_only_fields = ("id", "created_at", "updated_at")
        extra_fields = ("password", "employee_category", "zone", "store_name")

    def to_representation(self, instance):
        self.fields["zone"] = ZoneSerializer(read_only=True)
        self.fields["store_name"] = serializers.SerializerMethodField()
        return super(MerchantSerializer, self).to_representation(instance)

    def get_store_name(self, obj):
        partner = Partner.objects.get(users=obj.user)
        return partner.name


class MerchantApproveSerializer(serializers.Serializer):
    is_active = serializers.BooleanField(required=True)


class MerchantListSerializer(serializers.ModelSerializer):
    shop_details = serializers.SerializerMethodField(read_only=True)
    status_detail = serializers.CharField(source="get_status_display", read_only=True)
    class Meta:
        model = Employee
        fields = "__all__"
        read_only_fields = ("id", "is_active")

    def get_shop_details(self, obj):
        qs = Partner.objects.filter(users = obj.user).last()
        if qs:
            return {
                'id': qs.id,
                'name':qs.name,
                'partner_type':qs.partner_type.name,
                'logo': qs.logo.url if qs.logo else None,
            }
        return None
class MerchantSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6, write_only=True, required=True)
    last_name = serializers.CharField(max_length=50, required=True)
    user = serializers.CharField(read_only=True)
    employee_category = EmployeeCategorySerializer(read_only=True)
    zone = serializers.IntegerField()
    store_name = serializers.CharField(max_length=150)
    logo = Base64ImageField()
    image = Base64ImageField()
    zip_code = serializers.CharField(max_length=10)
    is_third_party_delivery = serializers.BooleanField(default=False)
    is_third_party_pickup = serializers.BooleanField(default=False)
    status_detail = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Employee
        depth = 1
        fields = "__all__"
        extra_fields = ("password", "user", "employee_category", "zone","store_name", "status_detail")
    

    def to_representation(self, instance):
        self.fields["zone"] = ZoneSerializer(read_only=True)
        return super(MerchantSerializer, self).to_representation(instance)

    def create(self, validated_data):
        image = validated_data.pop('image', None)
        if image:
            return Employee.objects.create(image=image, **validated_data)
        return ProductImage.objects.create(**validated_data)
        

class MerchantApproveSerializer(serializers.Serializer):
    status = serializers.CharField(required=True)


# class CustomUserAddressSerializer(serializers.ModelSerializer):
#     user = UserSerializerCustom(read_only=True)

#     class Meta:
#         model = UserAddress
#         fields = "__all__"


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        depth = 1
        fields = "__all__"
