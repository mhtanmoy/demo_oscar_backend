import re
from django.utils.text import slugify
from rest_framework import viewsets
from rest_framework.response import Response

from utils.custom_pagination import CustomPagination
from utils.response_wrapper import ResponseWrapper
from utils.custom_pagination import CustomPagination
from .models import Zone, SubZone
from .serializers import ZoneSerializer, SubZoneSerializer
from .models import Zone, Partner, PartnerType, SubZone
from .serializers import (
    ZoneSerializer,
    PartnerSerializer,
    PartnerTypeSerializer,
    SubZoneSerializer,
)
from rest_framework import status
from rest_framework.response import Response
from utils.custom_viewset import CustomViewSet
from rest_framework.permissions import *
from utils.response_wrapper import ResponseWrapper

from rest_framework import viewsets, serializers, filters
from django_filters.rest_framework import DjangoFilterBackend
from .filters import *
from accounts.models import UserAccount as User


class ZoneViewSet(CustomViewSet):
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer
    pagination_class = CustomPagination
    lookup_field = "pk"

    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_fields = ("title", "is_active")
    filterset_class = ZoneFilter 

    def create(self, request, *args, **kwargs):
        qs = self.get_queryset()
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)

        if serializer.is_valid():
            title = serializer.validated_data.get("title")
            address = serializer.validated_data.get("address")
            location = serializer.validated_data.get("location")
            city = serializer.validated_data.get("city")

            if not location:
                return ResponseWrapper(
                    error_msg="Location Not Given and also Location Must Be Polygon Field",
                    error_code=400,
                    status=400,
                )

            pattern = re.compile(r"[A-Za-z0-9-_]+")
            if not pattern.match(title):
                return ResponseWrapper(
                    error_msg="Please insert valid title", 
                    error_code=400,
                    status=400,
                )
            if not pattern.match(address):
                return ResponseWrapper(
                    error_msg="Please insert valid address",
                    error_code=400,
                    status=400,
                )
            if not pattern.match(city):
                return ResponseWrapper(
                    error_msg="Please insert valid city", 
                    error_code=400,
                    status=400,
                    )

            if not qs.filter(title__iexact=title).exists():
                try:
                    serializer.save()
                except:
                    return ResponseWrapper(
                        error_msg= "Please insert valid data",
                        error_code=400,
                        status=400,
                    )
                return ResponseWrapper(
                    data=serializer.data,
                    msg="Successfully Created",
                    status=200,
                )
            else:
                return ResponseWrapper(
                    error_msg="Zone title already exists",
                    error_code=400,
                    status=400,
                )
        else:
            return ResponseWrapper(
                error_msg= serializer.errors,
                error_code=400,
                status=400,
            )

    def update(self, request, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, partial=True)

        qs = self.queryset.filter(**kwargs)
        if not qs.exists():
            return ResponseWrapper(
                error_msg="Zone not found",
                error_code=404,
                status=404,
            )

        if serializer.is_valid():
            title = serializer.validated_data.get("title")
            if self.get_queryset().filter(title__iexact=title).exclude(id=kwargs.get("pk")).exists():
                return ResponseWrapper(
                    error_msg="Zone title already exists",
                    error_code=400,
                    status=400,
                )

            try:
                qs = serializer.update(
                    instance=self.get_object(), validated_data=serializer.validated_data
                )
                serializer = self.serializer_class(instance=qs)
            except:
                return ResponseWrapper(
                    error_msg="Please insert valid data",
                    error_code=400,
                    status=400,
                )
            return ResponseWrapper(
                data=serializer.data, 
                msg="Updated", 
                status=200
            )
        else:
            return ResponseWrapper(
                error_msg= serializer.errors, 
                error_code=400,
                status=400,    
            )

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        qs = self.get_queryset()

        zone = qs.filter(pk = pk)
        if not zone.exists():
            return ResponseWrapper(
                error_msg="Zone not found", 
                error_code=404,
                status=404,
            )

        serializer = self.get_serializer(zone.first())
        return ResponseWrapper(
            data=serializer.data,
            msg="Success",
            status=200,
        )

    def destroy(self, request, **kwargs):
        qs = self.queryset.filter(**kwargs)
        if qs:
            qs.first().delete()
            return ResponseWrapper(
                msg="Successfully Deleted",
                status=200,
            )
        else:
            return ResponseWrapper(
                error_msg="Zone not found",
                error_code=404,
                status=404,
            )

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        page_qs = self.paginate_queryset(qs)
        serializer = ZoneSerializer(instance=page_qs, many=True)
        paginated_data = self.get_paginated_response(serializer.data)
        return ResponseWrapper(data=paginated_data.data, msg='Success', status=200)


class SubZoneViewSet(CustomViewSet):
    queryset = SubZone.objects.all()
    serializer_class = SubZoneSerializer
    pagination_class = CustomPagination
    lookup_field = "pk"

    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_fields = ("title", "is_active","zone")
    filterset_class = SubZoneFilter 

    def create(self, request, *args, **kwargs):
        qs = self.get_queryset()
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)

        if serializer.is_valid():
            name = serializer.validated_data.get("name")

            pattern = re.compile(r"[A-Za-z0-9-_]+")
            if not pattern.match(name):
                return ResponseWrapper(
                    error_msg= "Please insert valid name", 
                    error_code=400, 
                    status=400
                )

            if not qs.filter(name__iexact=name).exists():
                try:
                    serializer.save()
                except:
                    return ResponseWrapper(
                        error_msg= "Please insert valid data", 
                        error_code=400,
                        status=400
                    )
                return ResponseWrapper(
                    data=serializer.data,
                    msg="Successfully Created",
                    status=201,
                )
            else:
                return ResponseWrapper(
                    error_msg= "Sub zone is already exists", 
                    error_code=400,
                    status=400    
                )
        else:
            return ResponseWrapper(
                error_msg=serializer.errors, 
                error_code=400,
                status=400
            )

    def update(self, request, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, partial=True)

        qs = self.queryset.filter(**kwargs) 
        if not qs.exists():
            return ResponseWrapper(
                error_msg="Sub Zone Not Found", 
                error_code=404,
                status=404,        
            )

        if serializer.is_valid():
            name = serializer.validated_data.get("name")
            if self.get_queryset().filter(name__iexact=name).exclude(id=kwargs.get("pk")).exists():
                return ResponseWrapper(
                    error_msg="Sub Zone name already exists", 
                    error_code=400,
                    status=400    
                )

            try:
                qs = serializer.update(
                    instance=self.get_object(), validated_data=serializer.validated_data
                )
                serializer = self.serializer_class(instance=qs)
            except:
                return ResponseWrapper(
                    error_msg= "Please insert valid data", 
                    error_code=400,
                    status=400    
                )
            return ResponseWrapper(
                data=serializer.data, 
                msg="Successfully Updated", 
                status=200
            )
        else:
            return ResponseWrapper(
                error_msg= serializer.errors, 
                error_code=400,
                status=400,
            )

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        qs = self.get_queryset()

        subzone = qs.filter(pk = pk)
        if not subzone.exists():
            return ResponseWrapper(
                error_msg="Sub Zone not found", 
                error_code=404,
                status=404,
            )

        serializer = self.get_serializer(subzone.first())
        return ResponseWrapper(
            data=serializer.data,
            msg="Success",
            status=200,
        )

    def destroy(self, request, **kwargs):
        qs = self.queryset.filter(**kwargs)
        if qs:
            qs.first().delete()
            return ResponseWrapper(
                msg="Successfully Deleted",
                status=200,
            )
        else:
            return ResponseWrapper(
                error_msg="Sub Zone not found",
                error_code=404,
                status=404,
            )

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        page_qs = self.paginate_queryset(qs)
        serializer = SubZoneSerializer(instance=page_qs, many=True)
        paginated_data = self.get_paginated_response(serializer.data)
        return ResponseWrapper(data = paginated_data.data, msg='Success', status=200)


class PartnerViewSet(CustomViewSet):
    queryset = Partner.objects.all().order_by("id")
    serializer_class = PartnerSerializer
    # permission_classes = (IsAuthenticated,)
    lookup_field = "pk"

    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_fields = ("grade", "partner_type","name")
    filterset_class = PartnerFilter 

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        page_qs = self.paginate_queryset(qs)
        serializer = PartnerSerializer(instance=page_qs, many=True)
        paginated_data = self.get_paginated_response(serializer.data)
        return ResponseWrapper(data = paginated_data.data, msg='Success')
 
    # def retrieve(self, request, *args, **kwargs):
    #     # pk = kwargs.get("pk")
    #     # if not pk:
    #     #     return ResponseWrapper(
    #     #         error_msg="Please provide partner id", 
    #     #         error_code=400,
    #     #         status=400
    #     #     )
    #     qs = self.get_queryset()

    #     object = qs.filter(pk = pk)
    #     if not object.exists():
    #         return ResponseWrapper(
    #             error_msg="Partner not found",
    #             error_code=404,
    #             status=404
    #         )

    #     serializer = self.get_serializer(object.first())
    #     return ResponseWrapper(
    #         data=serializer.data,
    #         msg="Success",
    #         status=200
    #     )

    # def update(self, request, **kwargs):
    #     serializer_class = self.get_serializer_class()
    #     serializer = serializer_class(data=request.data, partial=True)

    #     name = request.data.get('name')
    #     if name:
    #         partner_qs = Partner.objects.filter(name=name).last().exclude(**kwargs)
    #         if partner_qs:
    #             return ResponseWrapper(
    #                 error_msg="Partner name already exists", 
    #                 error_code=400,
    #                 status=400
    #             )
        
    #     zone = request.data.get('zone')
    #     if zone:
    #         zone_qs = Zone.objects.filter(id=zone).last()
    #         if not zone_qs:
    #             return ResponseWrapper(
    #                 error_msg="Zone Not Found",
    #                 error_code=404,
    #                 status=404
    #             )


    #     if serializer.is_valid():
    #         try:
    #             qs = serializer.update(
    #                 instance=self.get_object(), validated_data=serializer.validated_data
    #             )
    #             serializer = self.serializer_class(instance=qs)
    #         except:
    #             return ResponseWrapper(
    #                 error_msg= "Please insert valid data",
    #                 error_code=400,
    #                 status=400
    #             )
    #         return ResponseWrapper(data=serializer.data, msg="Updated", status=200)
    #     else:
    #         return ResponseWrapper(
    #             error_msg= serializer.errors,
    #             error_code=400,
    #             status=400
    #         )


    def create(self, request, *args, **kwargs):
        name = request.data.get("name")
        partner_type = request.data.get("partner_type")
        zone = request.data.get("zone")
        # user_list = request.data.get("users")
        # zip_code = request.data.get("zip_code")
        # is_third_party_delivery = request.data.get("is_third_party_delivery")
        # is_third_party_pickup = request.data.get("is_third_party_pickup")
        logo = request.data.get("logo")

        if not logo:
            return ResponseWrapper(
                error_msg="No Logo is provided", 
                error_code=400,
                status=400
            )
        grade = request.data.get("grade")

        partner_qs = Partner.objects.filter(name=name).last()
        if partner_qs:
            return ResponseWrapper(
                error_msg="Partner already exists", 
                error_code=400,
                status=400
            )

        if len(name.strip()) == 0:
            return ResponseWrapper(
                error_msg="Name is required",
                error_code=400,
                status=400
            )

        zone_qs = Zone.objects.filter(id=zone).last()
        if not zone_qs:
            return ResponseWrapper(
                error_msg="Zone Not Found",
                error_code=404,
                status=404
            )

        partner_type_qs = PartnerType.objects.filter(id=partner_type).last()
        if not partner_type_qs:
            return ResponseWrapper(
                error_msg="Partner Type Not Found", 
                error_code=404,
                status=404
            )

        if  grade not in ('A','B','C','D','OTHERS'):
            return ResponseWrapper(
                error_msg="Grade is not Valid",
                error_code=400,
                status=400
            ) 

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return ResponseWrapper(
                data=serializer.data,
                msg="Partner Created",
                status=201
            )
        else:
            return ResponseWrapper(
                error_msg= serializer.errors,
                error_code=400,
                status=400
            )

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        qs = self.get_queryset()

        partner = qs.filter(id = pk)
        if not partner.exists():
            return ResponseWrapper(
                error_msg="Partner not found", 
                error_code=404,
                status=404
            )

        serializer = self.get_serializer(partner.first())
        return ResponseWrapper(
            data=serializer.data,
            msg="Success",
            status=200
        )

    def update(self, request, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, partial=True)

        qs = self.queryset.filter(**kwargs)
        if not qs.exists():
            return ResponseWrapper(
                error_msg="Partner Not Found", 
                error_code=404,
                status=404
            )

        code = request.data.get("code")
        if code:
            return ResponseWrapper(
                error_msg="Code cannot be updated",
                error_code=400,
                status=400
            )

        zone = request.data.get('zone')
        if zone:
            zone_qs = Zone.objects.filter(id=zone).last()
            if not zone_qs:
                return ResponseWrapper(
                    error_msg="Zone Not Found",
                    error_code=404,
                    status=404
                )
        name = request.data.get("name")
        if name:
            if self.get_queryset().filter(name__iexact=name).exclude(id=kwargs.get("pk")).exists():
                return ResponseWrapper(
                    error_msg="Partner name already exists", 
                    error_code=400,
                    status=400
                )
            if len(name.strip()) == 0:
                return ResponseWrapper(
                    error_msg="Name is required",
                    error_code=400,
                    status=400
                )
        partner_type = request.data.get("partner_type")
        if partner_type:        
            partner_type_qs = PartnerType.objects.filter(id=partner_type).last()
            if not partner_type_qs:
                return ResponseWrapper(
                    error_msg="Partner Type Not Found", 
                    error_code=404,
                    status=404
                )

        grade = request.data.get("grade")
        if grade:
            if  grade not in ('A','B','C','D','OTHERS'):
                return ResponseWrapper(
                    error_msg="Grade is not Valid",
                    error_code=400,
                    status=400
                ) 

        if serializer.is_valid():
            users = request.data.get("users")
            qs = serializer.update(instance=self.get_object(), validated_data=serializer.validated_data)
            qs.code = slugify(qs.name)
            if users:
                # valid user or not
                for user in users:
                    if not User.objects.filter(id=user).exists():
                        return ResponseWrapper(
                            error_msg="User not found", 
                            error_code=404,
                            status=404
                        )
                qs.users.set(users)
            qs.save()
            serializer = self.serializer_class(instance=qs)
            return ResponseWrapper(
                data=serializer.data, 
                msg="Updated",
                status=200
            )
        else:
            return ResponseWrapper(
                error_msg=serializer.errors, 
                error_code=400,
                status=400
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
                error_msg="Partner Not Found",
                error_code=404,
                status=404
            )

    def approved_partners(self, request, **kwargs):
        partner_qs = Partner.objects.filter(users__is_active=True) ## User of the Partner is Approved, True
        if not partner_qs:
            return ResponseWrapper(
                error_msg="No Active Partner Found",
                error_code=404,
                status=404
            )
        page_qs = self.paginate_queryset(partner_qs)
        serializer = PartnerSerializer(instance=page_qs, many=True)
        paginated_data = self.get_paginated_response(serializer.data)
        return ResponseWrapper(data=paginated_data.data, msg='Success')
        
class PartnerTypeViewSet(CustomViewSet):
    queryset = PartnerType.objects.all()
    serializer_class = PartnerTypeSerializer
    lookup_field = "pk"

    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_fields = ("name", "slug")
    filterset_class = PartnerTypeFilter 

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        page_qs = self.paginate_queryset(qs)
        serializer = PartnerTypeSerializer(instance=page_qs, many=True)
        paginated_data = self.get_paginated_response(serializer.data)
        return ResponseWrapper(data = paginated_data.data, msg='Success')


    def create(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        if serializer.is_valid():
            name = request.data.get('name')
            if not name:
                return ResponseWrapper(error_msg='Name is Required', error_code=400, status=400)
            partner_type_qs = PartnerType.objects.filter(name=name).last()
            if partner_type_qs:
                return ResponseWrapper(error_msg='Partner Type is Already Found', error_code=400, status=400)
            qs = serializer.save()
            return ResponseWrapper(data=serializer.data, msg='created', status=201)
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400, status=400)
    def update(self, request,pk, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, partial=True)
        if serializer.is_valid():
            name = request.data.get('name')
            if not name:
                return ResponseWrapper(error_msg='Name is Required', error_code=400, status=400)
            partner_type_qs = PartnerType.objects.filter(name=name).exclude(id = pk).last()
            if partner_type_qs:
                return ResponseWrapper(error_msg='Partner Type is Already Found', error_code=400, status=400)

            qs = serializer.update(instance=self.get_object(
            ), validated_data=serializer.validated_data)
            serializer = self.serializer_class(instance=qs)
            return ResponseWrapper(data=serializer.data, msg='updated', status=200)
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400, status=400)
