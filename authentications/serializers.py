from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model, authenticate, password_validation
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import UserAccount as User
from accounts.models import CustomerInfo
from apps.partner.models import Partner
from django.contrib.auth.models import Group, Permission

from accounts.models import Employee, EmployeeCategory
from drf_extra_fields.fields import Base64FileField, Base64ImageField

class FollowedStoreSerializer(serializers.ModelSerializer):
    store_id = serializers.IntegerField(source='partner.id')
    class Meta:
        model = Partner
        fields = ['store_id']


class CustomerInfoSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = CustomerInfo
        fields = ['id', 'user', 'followed_store', 'gender', 'image', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', '']
       
    def create(self, validated_data):
        image = validated_data.pop('image', None)
        if image:
            return CustomerInfo.objects.create(image=image, **validated_data)
        return CustomerInfo.objects.create(**validated_data)


class UserSerializerCustom(serializers.ModelSerializer):
    customer_info = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'date_joined', 'phone', 'is_block', 'customer_info']
        read_only_fields = ['id', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'date_joined']

    def get_customer_info(self, obj):
        try:
            customer_info = CustomerInfo.objects.filter(user=obj).first()
            return CustomerInfoSerializer(customer_info).data
        except:
            return None
    
class UserSerializerWithToken(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email','phone', 'token', 'is_block']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'phone', 'password', 'first_name', 'last_name']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    
class BlockUserSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source='user.id')
    class Meta:
        model = User
        fields = ['user']




class LoginSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()
    # partner_id = serializers.SerializerMethodField()
    # partner_name = serializers.SerializerMethodField()
    # employee_category = serializers.SerializerMethodField()
    partner = serializers.SerializerMethodField()
    permission_list = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['username', 'email', 'phone','token', 'partner', 'permission_list']
        #extra_fields = ['partner_id', 'partner_name', 'employee_category', 'permission_list']

    def get_permission_list(self, obj):
        permissions = obj.user_permissions.all()
        permission_list = []
        for permission in permissions:
            permission_list.append(permission.name)
        return permission_list

    # def get_employee_category(self, obj):
    #     employee = Employee.objects.filter(user=obj).first()
    #     if employee:
    #         if not employee.employee_category.name == 'Merchant':
    #             return employee.employee_category.name
    #         else:
    #             return None
    #     else:
    #         return None

    # def get_partner_id(self, obj):
    #     employee = Employee.objects.filter(user=obj).first()
    #     if employee:
    #         if employee.employee_category.name == 'Merchant':
    #             partner = Partner.objects.filter(users=obj).first()
    #             return partner.id
    #         else:
    #             return None
    #     else:
    #         return None

    # def get_partner_name(self, obj):
    #     employee = Employee.objects.filter(user=obj).first()
    #     if employee:
    #         if employee.employee_category.name == 'Merchant':
    #             partner = Partner.objects.filter(users=obj).first()
    #             return partner.name
    #         else:
    #             return None
    #     else:
    #         return None
    def get_partner(self, obj):
        employee = Employee.objects.filter(user=obj).first()
        if employee:
            if employee.employee_category.name == 'Merchant':
                partner = Partner.objects.filter(users=obj).first()
                return {
                    'id': partner.id,
                    'name': partner.name,
                    'employee_category': employee.employee_category.name
                }
            else:
                return {
                    'id': None,
                    'name': None,
                    'employee_category': employee.employee_category.name,
                }
        else:
            return None
    
    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)

class LoginSerializerCustom(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['username',]
        extra_kwargs = {
            'password': {'write_only': True}
        }

class ChangePasswordSerializer(serializers.Serializer):
    username = serializers.CharField()
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    class Meta:
        model = User
        fields = ['username', 'old_password', 'new_password']


class ForgotPasswordSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    class Meta:
        model = User
        fields = ['username','new_password']

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename']

class GroupSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions']

class PermissionAddSerializer(serializers.Serializer):
    permissions = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    user = serializers.IntegerField(write_only=True)

class UserPermissionSerializer(serializers.Serializer):
    user = serializers.IntegerField(write_only=True)

class GroupCustomSerializer(serializers.Serializer):
    name = serializers.CharField()
    permissions = serializers.ListField(child=serializers.IntegerField(), write_only=True)