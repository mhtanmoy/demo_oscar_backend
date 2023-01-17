from django.shortcuts import get_object_or_404
from django.db import transaction
from oscar.apps.address.models import UserAddress
from oscar_accounts import models
from rest_framework import viewsets
from rest_framework.response import Response
from django.db.models import Q
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAdminUser, AllowAny
from django.contrib.auth.models import Group, Permission
from django.contrib import auth

from utils import custom_viewset
from .models import Employee, EmployeeCategory
from .serializers import *
from .permissions import IsAdminOrAuthenticated

from apps.partner.models import Partner, PartnerType, Zone
from apps.order.models import Order
from oscar.apps.order.models import Line
from rest_framework.permissions import IsAuthenticated
from accounts.models import UserAccount

from rest_framework import status, filters
from rest_framework.response import Response
from utils.custom_viewset import CustomViewSet
from utils.response_wrapper import ResponseWrapper
from django.shortcuts import get_object_or_404
from apps.partner.models import Partner, PartnerType, Zone
from django_filters.rest_framework import DjangoFilterBackend
from .filters import EmployeeFilter
from django.db.models import Q


# User model
User = get_user_model()
import re


class AccountViewSet(CustomViewSet):
    queryset = models.Account.objects.all()
    serializer_class = AccountSerializer


class EmployeeCategoryViewSet(CustomViewSet):
    queryset = EmployeeCategory.objects.all()
    serializer_class = EmployeeCategorySerializer
    # permission_classes = [IsAdminOrAuthenticated]
    lookup_field = "pk"

    def create(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data.get("name")

            # Group create
            g, created = Group.objects.get_or_create(name=name)

            qs = serializer.save()
            return ResponseWrapper(data=serializer.data, msg="created")
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400, status=400)


class EmployeeViewSet(CustomViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    lookup_field = "pk"

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        if serializer.is_valid():
            first_name = serializer.validated_data.get("first_name")
            last_name = serializer.validated_data.get("last_name")
            email = serializer.validated_data.get("email")
            phone = serializer.validated_data.get("phone")
            password = serializer.validated_data.pop("password")

            pattern = re.compile(r"[A-Za-z0-9-_]+")
            if not pattern.match(first_name):
                return ResponseWrapper(error_msg="Please Insert Valid First Name", error_code=400, status=400)
            if not pattern.match(last_name):
                return ResponseWrapper(error_msg="Please Insert valid Last Name", error_code=400, status=400)

            existing_user = User.objects.filter(
                Q(email__exact=email) | Q(phone__exact=phone)
            ).exists()
            if existing_user:
                return ResponseWrapper(error_msg="Try with different email or phone", error_code=400, status=400)

            # Creating User
            new_user = User.objects.create_user(
                username=email,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                password=password,
            )

            serializer.save(user=new_user)
            return ResponseWrapper(data=serializer.data, msg="Created", status=201)
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400, status=400)

    def list(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        qs = self.get_queryset()
        page_qs = self.paginate_queryset(qs)
        serializer = serializer_class(instance=page_qs, many=True)
        paginated_data = self.get_paginated_response(serializer.data)

        return ResponseWrapper(data=paginated_data.data, msg='Success')

    def update(self, request, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, partial=True)

        qs = self.queryset.filter(**kwargs)
        if not qs.exists():
            return ResponseWrapper(
                error_msg="Employee Not Found", 
                error_code=404,
                status=404
            )
        
        if serializer.is_valid():
            qs = serializer.update(instance=self.get_object(
            ), validated_data=serializer.validated_data)
            serializer = self.serializer_class(instance=qs)

            return ResponseWrapper(data=serializer.data, msg='updated', status=200)
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400, status=400)

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        qs = self.get_queryset()

        employee = qs.filter(id = pk)
        if not employee.exists():
            return ResponseWrapper(
                error_msg="Employee not found", 
                error_code=404,
                status=404
            )

        serializer = self.get_serializer(employee.first())
        return ResponseWrapper(
            data=serializer.data,
            msg="Success",
            status=200
        )

    def destroy(self, request, **kwargs):
        qs = self.queryset.filter(**kwargs).first()
        if qs:
            qs.delete()
            return ResponseWrapper(
                msg="deleted",
                status=200
            )
        else:
            return ResponseWrapper(
                error_msg="Employee not found",
                error_code=404,
                status=404
            )


# class UserAddressViewSet(CustomViewSet):
#     queryset = UserAddress.objects.all()
#     serializer_class = UserAddressSerializer
#     lookup_field = "pk"
#     #permission_classes = IsAuthenticated


class MerchantViewSet(CustomViewSet):
    queryset = Employee.objects.all()
    serializer_class = MerchantListSerializer
    lookup_field = "pk"
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_fields = ('is_active')
    filterset_class = EmployeeFilter

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [IsAuthenticated]
        elif self.action == "approve":
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'create':
            self.serializer_class = MerchantSerializer

        elif self.action == 'approve':
            self.serializer_class = MerchantApproveSerializer
        else:
            self.serializer_class = MerchantListSerializer

        return self.serializer_class

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        qs = qs.filter(employee_category__name__icontains="Merchant")

        page_qs = self.paginate_queryset(qs)
        serializer = MerchantListSerializer(instance=page_qs, many=True)
        paginated_data = self.get_paginated_response(serializer.data)
        return ResponseWrapper(data=paginated_data.data, msg="Success")

    def create(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        if not serializer.is_valid():
            return ResponseWrapper(error_msg=serializer.errors, error_code=400,status=400)

        # if serializer.is_valid():
        first_name = serializer.validated_data.get("first_name")
        last_name = serializer.validated_data.get("last_name")
        email = serializer.validated_data.get("email")
        phone = serializer.validated_data.get("phone")
        password = serializer.validated_data.pop("password")
        zone = serializer.validated_data.get("zone")
        nid = serializer.validated_data.get("nid")
        employee_category = serializer.validated_data.get("employee_category")
        shift_start_hour = serializer.validated_data.get("shift_start_hour")
        shift_end_hour = serializer.validated_data.get("shift_end_hour")
        date_of_birth = serializer.validated_data.get("date_of_birth")
        image = serializer.validated_data.get("image")
        store_name = serializer.validated_data.pop("store_name")

        logo = serializer.validated_data.pop("logo")
        zip_code = serializer.validated_data.pop("zip_code")
        is_third_party_delivery = serializer.validated_data.pop("is_third_party_delivery")
        is_third_party_pickup = serializer.validated_data.pop("is_third_party_pickup")

        pattern = re.compile(r"[A-Za-z0-9-_]+")
        if not pattern.match(first_name):
            return ResponseWrapper(
                error_msg="Please Insert Valid First Name",status=400
            )
        if not pattern.match(last_name):
            return ResponseWrapper(
                error_msg="Please Insert valid Last Name",status=400
            )

        existing_user = User.objects.filter(
            Q(email__exact=email) | Q(phone__exact=phone)
        ).exists()
        if existing_user:
            return ResponseWrapper(
                error_msg="Try with different email or phone",status=400
            )

        # Zone
        zone_qs = Zone.objects.filter(id=zone).last()

        if not zone_qs:
            return ResponseWrapper(
                error_msg="Zone not found",
                status=404
            )

        # create partner
        market_place_qs = PartnerType.objects.filter(name__icontains="Marketplace").last()
        if not market_place_qs:
            return ResponseWrapper(
                error_msg="Marketplace not found",
                status=404
            )

        # merchant
        merchant_qs = EmployeeCategory.objects.filter(name__icontains="Merchant").last()
        if not merchant_qs:
            return ResponseWrapper(
                error_msg="Merchant not found",
                status=404
            )

        partner_in_same_name = Partner.objects.filter(name=store_name).last()
        if partner_in_same_name:
            return ResponseWrapper(
                error_msg="Store with this name is already exist.",
                status=404
            )
        with transaction.atomic():
        # Creating User
            new_user = User.objects.create_user(
                username=email,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                password=password,
            )

            # Creating Partner
            partner = Partner.objects.create(
                partner_type_id=market_place_qs.id,
                zone_id=zone_qs.id,
                name=store_name,
                logo=logo,
                zip_code=zip_code,
                is_third_party_delivery=is_third_party_delivery,
                is_third_party_pickup=is_third_party_pickup,
                is_active=False,
            )
            # assign new_user to partner
            partner.users.add(new_user)

            # Creating Employee
            new_employee = Employee.objects.create(
                user=new_user,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                shift_start_hour=shift_start_hour,
                shift_end_hour=shift_end_hour,
                date_of_birth=date_of_birth,
                image=image,
                employee_category=merchant_qs,
                nid=nid,
                status="PENDING",
            )

            serializer = MerchantListSerializer(instance=new_employee)
            return ResponseWrapper(
                data=serializer.data,
                msg="Success",
                status=201
            )
            
    def update(self, request, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, partial=True)

        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        email = request.data.get("email")
        phone = request.data.get("phone")
        zone = request.data.get("zone")
        #store_name = request.data.pop("store_name")

        pattern = re.compile(r"[A-Za-z0-9-_]+")
        if first_name:
            if not pattern.match(first_name):
                return ResponseWrapper(
                    error_msg="Please Insert Valid First Name",status=400
                )
                
        if last_name:
            if not pattern.match(last_name):
                return ResponseWrapper(
                    error_msg="Please Insert valid Last Name",status=400
                )

        if phone:
            existing_user = User.objects.filter(
                phone__exact=phone).exclude(**kwargs).exists()

            if existing_user:
                return ResponseWrapper(
                    error_msg="Try with different phone",status=400
                )

        if email:
            existing_user = User.objects.filter(
                email__exact=email).exclude(**kwargs).exists()

            if existing_user:
                return ResponseWrapper(
                    error_msg="Try with different email",status=400
                )       
        #Zone
        if zone:
            zone_qs = Zone.objects.filter(id=zone).last()
            if not zone_qs:
                return ResponseWrapper(
                    error_msg="Zone not found",
                    status=404
                )

        if serializer.is_valid():
            qs = serializer.update(instance=self.get_object(
            ), validated_data=serializer.validated_data)
            serializer = self.serializer_class(instance=qs)
            return ResponseWrapper(data=serializer.data,status=200)
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400)


    def approve(self, request, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, partial=True)

        if serializer.is_valid():
            pk = kwargs.get("pk")
            status = serializer.validated_data.get("status")
            if not status:
                return ResponseWrapper(
                    error_msg="Status is required",
                    status=400
                )

            if request.user.employees.filter(employee_category__name__icontains="Portfolio Manager").exists():
                emp = Employee.objects.filter(id=pk).last()
                if not emp:
                    return ResponseWrapper(
                        error_msg="Employee not found",
                        status=404
                    )

                if status == emp.status:
                    return ResponseWrapper(
                        error_msg=f'This employee is already {status}',
                        status=400
                    )

                if status == "REJECTED" or status == "BLOCKED":
                    user = emp.user
                    partner = Partner.objects.filter(users=user).last()
                    line = Line.objects.filter(partner=partner, status__in=["Initialized","Pending", "Placed","Confirm"]).last()
                    if line:
                        return ResponseWrapper(
                            error_msg="This merchant has already a order",
                            status=400
                        )
                    emp.status = status
                    emp.save()
                elif status == "ACCEPT" or status == "PENDING":

                    emp.status = status
                    emp.save()
                else:
                    return ResponseWrapper(
                        error_msg="Status is not valid",
                        status=400
                    )                

                serializer = MerchantListSerializer(instance=emp)

                return ResponseWrapper(data=serializer.data,msg='Merchant Approved Successfully',status=200)
            else:
                return ResponseWrapper(
                    error_code=400,
                    error_msg='Only Portfolio Manager can approve merchant',
                    status=400,
                )
        else:
            return ResponseWrapper(
                error_msg=serializer.errors,
                error_code=400,
                status=400,
            )
            

            

class GetAllPermissionsViewSet(CustomViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = Permission.objects.all()
        model = self.request.query_params.get("model")
        if model is not None:
            queryset = queryset.filter(codename__icontains=model)
        return queryset
