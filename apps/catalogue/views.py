import datetime, pytz
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from rest_framework import viewsets, serializers, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from django.db.models import Q
from oscar.apps.catalogue.models import (
    ProductClass,
    ProductAttribute,
    ProductAttributeValue,
)
from oscarapi.serializers.product import ProductAttributeValueSerializer
from drf_haystack.viewsets import HaystackViewSet
from haystack.query import SearchQuerySet
from drf_haystack.viewsets import HaystackViewSet
from utils.response_wrapper import ResponseWrapper
from utils.custom_pagination import CustomPagination


from apps.partner.models import Partner
from oscar.apps.partner.models import StockRecord

from utils.custom_viewset import CustomViewSet
from utils.response_wrapper import ResponseWrapper
from .models import Product, Discount, PromoCode, Category
from .serializers import *
from .permissions import IsDepoManager
from accounts.models import Employee, EmployeeCategory
from accounts.models import UserAccount as User
from .filters import *
import re
from django.utils.text import slugify
class ProductViewSet(CustomViewSet):
    serializer_class = CustomProductSerializer
    queryset = Product.objects.all()
    lookup_fields = "pk"
    # filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    # filterset_fields = ("title", "slug")
    filterset_class = ProductFilter

    # def get_permissions(self):
    #     if self.action == "create":
    #         permission_classes = [IsAuthenticated]
    #     else:
    #         permission_classes = [AllowAny]
    #     return [permission() for permission in permission_classes]


    def destroy(self, request, **kwargs):
        qs = self.queryset.filter(**kwargs).first()
        if qs:
            qs.delete()
            return ResponseWrapper(status=200, msg='deleted')
        else:
            return ResponseWrapper(error_msg="Product not found", error_code=404, status=404)

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        page_qs = self.paginate_queryset(qs)
        serializer = CustomProductListSerializer(instance=page_qs, many=True, context={"request": request})
        paginated_data = self.get_paginated_response(serializer.data)
        return ResponseWrapper(data = paginated_data.data, msg='Success')


    def create(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)

        if serializer.is_valid():
            qs = serializer.save()
            return ResponseWrapper(data=serializer.data, msg='created', status=201)
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400, status=400)

    def update(self, request, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, partial=True)

        qs = self.queryset.filter(**kwargs)
        if not qs.exists():
            return ResponseWrapper(
                error_msg="Product Not Found", 
                error_code=404,
                status=404
            )
            
        if serializer.is_valid():
            qs = serializer.update(instance=self.get_object(
            ), validated_data=serializer.validated_data)
            serializer = self.serializer_class(instance=qs, context={"request": request})
            return ResponseWrapper(data=serializer.data, msg='updated', status=200)
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400, status=400)
        
    def retrieve(self, request, *args, **kwargs):
        if kwargs["pk"].isdigit():
            pk = kwargs["pk"]
            qs = self.get_queryset()
            instance = qs.filter(id=pk)
            if not instance.exists():
                return ResponseWrapper(error_msg="Product not found", error_code=404, status=404)
            serializer = self.get_serializer(instance.first())
            return ResponseWrapper(data = serializer.data, msg="Product Details")
        else:
            slug = kwargs["pk"]
            qs = self.get_queryset()
            instance = qs.filter(slug__iexact=slug)
            if not instance.exists():
                return ResponseWrapper(error_msg="Product not found", error_code=404, status=404)
            serializer = self.get_serializer(instance.first())
            return ResponseWrapper(data = serializer.data, msg="Product Details")

    def product_details(self, request,slug, *args, **kwargs):
        qs = Product.objects.filter(slug = slug).last()
        if not qs:
            return ResponseWrapper(error_code=400, error_msg='Product Not Found')
        serializer  = CustomProductSerializer(instance=qs)
        return ResponseWrapper(data = serializer.data, msg="Product Details")


class ProductTypeViewSet(viewsets.ModelViewSet):
    serializer_class = CustomProductTypeSerializer
    queryset = ProductClass.objects.all()
    lookup_field = 'pk'
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_fields = ("name", "slug")
    filterset_class = ProductClassFilter

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        serializer_class = self.get_serializer_class()
        page_qs = self.paginate_queryset(qs)
        serializer = serializer_class(instance=page_qs, many=True, context={"request": request})
        paginated_data = self.get_paginated_response(serializer.data)
        return ResponseWrapper(data=paginated_data.data, msg="Success")

    def create(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)

        if serializer.is_valid():
            name = serializer.validated_data.get("name", None)
            if name:
                if self.get_queryset().filter(name__iexact=name).exists():
                    return ResponseWrapper(error_msg="Name already exists", error_code=400, status=400)
            qs = serializer.save()
            return ResponseWrapper(data=serializer.data, msg='created', status=201)
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400, status=400)

    def update(self, request, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, partial=True)

        qs = self.queryset.filter(**kwargs)
        if not qs.exists():
            return ResponseWrapper(
                error_msg="Product Class Not Found", 
                error_code=404,
                status=404
            )
        
        name = request.data.get("name", None)
        if name:
            if self.get_queryset().filter(name__iexact=name).exclude(id=kwargs["pk"]).exists():
                return ResponseWrapper(error_msg="Name already exists", error_code=400, status=400)
            
        if serializer.is_valid():
            qs = serializer.update(instance=self.get_object(
            ), validated_data=serializer.validated_data)
            qs.slug = slugify(qs.name)
            qs.save()
            serializer = self.serializer_class(instance=qs)

            return ResponseWrapper(data=serializer.data, msg='updated', status=200)
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400, status=400)
        
    def retrieve(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        qs = self.get_queryset()
        instance = qs.filter(id=pk)
        if not instance.exists():
            return ResponseWrapper(error_msg="Product Class not found", error_code=404, status=404)
        serializer = self.get_serializer(instance.first())
        return ResponseWrapper(data = serializer.data, msg="Product Details")

    def destroy(self, request, **kwargs):
        qs = self.queryset.filter(**kwargs).first()
        if qs:
            qs.delete()
            return ResponseWrapper(status=200, msg='deleted')
        else:
            return ResponseWrapper(error_msg='Product Class Not Found', error_code=404, status=404)

class ProductAttributeViewSet(viewsets.ModelViewSet):
    serializer_class = CustomProductAttributeSerializer
    queryset = ProductAttribute.objects.all()
    lookup_field = 'pk'
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_fields = ("name", "code")
    filterset_class = ProductAttributeFilter

    def get_serializer_class(self):
        if self.action == 'create':
            self.serializer_class = SimpleProductAttributeSerializer
        else:
            self.serializer_class = CustomProductAttributeSerializer

        return self.serializer_class

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        serializer_class = self.get_serializer_class()
        page_qs = self.paginate_queryset(qs)
        serializer = serializer_class(instance=page_qs, many=True, context={"request": request})
        paginated_data = self.get_paginated_response(serializer.data)
        return ResponseWrapper(data=paginated_data.data, msg="Success")

    def create(self, request, product_class_id, *args, **kwargs):
        serializer_class = SimpleProductAttributeSerializer

        product_class_qs = ProductClass.objects.filter(id= product_class_id).last()
        if not product_class_qs:
            return ResponseWrapper(error_msg='Product Class id is not valid', error_code=400, status=400)

        data=request.data
        # pattern = re.compile(r"[a-zA-Z_][0-9a-zA-Z_]+")
        types = ['text','integer','boolean', 'float', 'richtext' ,'date', 'datetime','option' , 'multi_option','entity','file', 'image']
        
        for item in data:
            if not item['type'] in types:
                return ResponseWrapper(error_msg='Type is not valid', error_code=400, status=400)

            # if not pattern.match(item['code']):
            #     return ResponseWrapper(error_msg='Code is not valid', error_code=400, status=400)

            item['product_class']= product_class_qs
            item['code']= slugify(item['name'])


        serializer = serializer_class(data=data, many = True)
        if serializer.is_valid():
            qs = []
            for item in data:
                item_qs = ProductAttribute.objects.create(**item)
                qs.append(item_qs)
            serializer = SimpleProductAttributeSerializer(qs, many =True)
            return ResponseWrapper(data=serializer.data, msg='created', status=201)
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400, status=400)

    def update(self, request, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, partial=True)

        qs = self.queryset.filter(**kwargs)
        if not qs.exists():
            return ResponseWrapper(
                error_msg="Product Attribute Not Found", 
                error_code=404,
                status=404
            )

        type = request.data.get('type')
        if type:
            types_list = ('text','integer','boolean', 'float', 'richtext' ,'date', 'datetime','option' , 'multi_option','entity','file', 'image')
            if not type in types_list:
                return ResponseWrapper(error_msg='Type is not valid', error_code=400, status=400)
        
        product_class_id = request.data.get('product_class_id')
        if product_class_id:        
            product_class_qs = ProductClass.objects.filter(id= product_class_id).last()
            if not product_class_qs:
                return ResponseWrapper(error_msg='Product Class id is not valid', error_code=400, status=400)
        
        code = request.data.get('code')
        if code:
            pattern = re.compile(r"[a-zA-Z_][0-9a-zA-Z_]+")
            if not pattern.match(code):
                return ResponseWrapper(error_msg='Code is not valid', error_code=400, status=400)
       
        if serializer.is_valid():
            qs = serializer.update(instance=self.get_object(
            ), validated_data=serializer.validated_data)
            serializer = self.serializer_class(instance=qs)
            return ResponseWrapper(data=serializer.data, msg='updated', status=200)
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400, status=400)
        
    def retrieve(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        qs = self.get_queryset()
        instance = qs.filter(id=pk)
        if not instance.exists():
            return ResponseWrapper(error_msg="Product Attribute not found", error_code=404, status=404)
        serializer = self.get_serializer(instance.first())
        return ResponseWrapper(data = serializer.data, msg="Product attribute Details")

    def destroy(self, request, **kwargs):
        qs = self.queryset.filter(**kwargs).first()
        if qs:
            qs.delete()
            return ResponseWrapper(status=200, msg='deleted')
        else:
            return ResponseWrapper(error_msg='Product Attribute Not Found', error_code=404, status=404)

class ProductAttributeValueViewSet(viewsets.ModelViewSet):
    serializer_class = CustomProductAttributeValueSerializer
    queryset = ProductAttributeValue.objects.all()
    lookup_field = 'pk'
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_fields = ("product__id")
    filterset_class = ProductAttributeValueFilter

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        serializer_class = self.get_serializer_class()
        page_qs = self.paginate_queryset(qs)
        serializer = serializer_class(instance=page_qs, many=True, context={"request": request})
        paginated_data = self.get_paginated_response(serializer.data)
        return ResponseWrapper(data=paginated_data.data, msg="Success")
    
    def create(self, request, product_id,*args, **kwargs):
        serializer_class = self.get_serializer_class()       
        product_qs = Product.objects.filter(id=product_id).last()
        data_item = request.data
        if not product_qs:
            return ResponseWrapper(error_msg='Product is not found', error_code=404, status=404)
        # for item in data_item:
        #     if ProductAttributeValue.objects.filter(product=product_id, attribute=item['attribute']).exists():
        #         return ResponseWrapper(error_msg="Attribute is already associated with Product,Use update", error_code=400, status=400)

        # for item in data_item:
        #     item['product']= product_id
        # serializer = serializer_class(data=data_item, many = True)
        # if serializer.is_valid():
        #     qs = serializer.save()
        # #qs=[]
        for item in data_item:
            if ProductAttributeValue.objects.filter(product=product_id, attribute=item['attribute']).exists():
                pav = ProductAttributeValue.objects.filter(product=product_id, attribute=item['attribute']).first()
                if not item['value'] is None:
                    pav.value = item['value']
                    pav.save()
                   # qs.append(pav)
                else:
                    return ResponseWrapper(error_msg="Value is not provided", error_code=400, status=400)
        qs= Product.objects.filter(id=product_id).first()
        serializer = CustomProductSerializer(qs,context={'request': request})
        return ResponseWrapper(data=serializer.data, msg='Values Updated', status=200)
        # else:
        #     return ResponseWrapper(error_msg=serializer.errors, error_code=400, status=400)


    def update(self, request,pk,  **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, partial=True)

        qs = self.queryset.filter(**kwargs)
        if not qs.exists():
            return ResponseWrapper(
                error_msg="Product Attribute Value Not Found", 
                error_code=404,
                status=404
            )

        product = request.data.get("product")
        attribute = request.data.get("attribute")
        value = request.data.get("value")

        if not product:
            return ResponseWrapper(error_msg="Please enter product field", error_code=400, status=400)

        if not attribute:
            return ResponseWrapper(error_msg="Please enter attribute field", error_code=400, status=400)

        if not value:
            return ResponseWrapper(error_msg="Please enter value field", error_code=400, status=400)

        if ProductAttributeValue.objects.filter(product=product, attribute=attribute).exists():
            pav = ProductAttributeValue.objects.filter(product=product, attribute=attribute).first()
            pav.value = value
            pav.save()
            serializer = ProductAttributeValueSerializer(instance=pav)
            return ResponseWrapper(data=serializer.data, msg="updated")
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=404, status=404)
        
        # if serializer.is_valid():
        #     qs = serializer.update(instance=self.get_object(
        #     ), validated_data=serializer.validated_data)
        #     serializer = self.serializer_class(instance=qs)

        #     return ResponseWrapper(data=serializer.data, msg='updated', status=200)
        # else:
        #     return ResponseWrapper(error_msg=serializer.errors, error_code=400, status=400)
        
    def retrieve(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        qs = self.get_queryset()
        instance = qs.filter(id=pk)
        if not instance.exists():
            return ResponseWrapper(error_msg="Product Attribute Value not found", error_code=404, status=404)
        serializer = self.get_serializer(instance.first())
        return ResponseWrapper(data = serializer.data, msg="Product attribute Value Details")

    def destroy(self, request, **kwargs):
        qs = self.queryset.filter(**kwargs).first()
        if qs:
            qs.delete()
            return ResponseWrapper(status=200, msg='deleted')
        else:
            return ResponseWrapper(error_msg="Not Found", error_code=404, status=404)



# service_id = 1
# market_place_id = 2
# daily_need_id = 3
class ServiceTypeProductViewSet(viewsets.ModelViewSet):
    serializer_class = CustomProductSerializer

    def get_queryset(self):
        partner = Partner.objects.get(partner_type__id=1)
        # if not partner:
        #     return ResponseWrapper(error_msg="There is no Partner under Service Category", error_code=400)
        return partner.zone.products.all()

class MarketPlaceTypeProductViewSet(viewsets.ModelViewSet):
    serializer_class = CustomProductSerializer

    def get_queryset(self):
        partner = Partner.objects.get(partner_type__id=2)
        return partner.zone.products.all()

class DailyNeedTypeProductViewSet(viewsets.ModelViewSet):
    serializer_class = CustomProductSerializer

    def get_queryset(self):
        partner = Partner.objects.get(partner_type__id=3)
        return partner.zone.products.all()


class ProductSearchViewSet(HaystackViewSet):
    index_models = [Product]
    serializer_class = ProductSearchSerializer


class ApproveProductView(viewsets.ModelViewSet):
    serializer_class = ApproveProductSerializer 
    # permission_classes = [IsDepoManager]
    queryset = Product.objects.all()
    lookup_field = "pk"

    def create(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        if serializer.is_valid():
            qs = serializer.save()
            return ResponseWrapper(data=serializer.data, msg='created', status=201)
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400, status=400)


class ProductStockRecordViewSet(viewsets.ModelViewSet):
    serializer_class = CustomProductStockRecordSerializer
    queryset = StockRecord.objects.all()
    lookup_field = "pk"
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_fields = ("product__id")
    filterset_class = StockRecordFilter

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        serializer_class = self.get_serializer_class()
        page_qs = self.paginate_queryset(qs)
        serializer = serializer_class(instance=page_qs, many=True, context={"request": request})
        paginated_data = self.get_paginated_response(serializer.data)
        return ResponseWrapper(data=paginated_data.data, msg="Success")
    
    def create(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        if serializer.is_valid():
            product = serializer.validated_data.get("product")
            if product.structure == "parent":
                return ResponseWrapper(error_msg="Parent product can not have stockrecord", error_code=400, status=400)
            stockrecord = StockRecord.objects.filter(product_id=product.id)
            if stockrecord.exists():
                return ResponseWrapper(error_msg="Product stockrecord already exists", error_code=400, status=400)

            qs = serializer.save()
            return ResponseWrapper(data=serializer.data, msg='created', status=201)
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400, status=400)

    def update(self, request, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, partial=True)

        qs = self.queryset.filter(**kwargs)
        if not qs.exists():
            return ResponseWrapper(
                error_msg="Product Stock records Not Found", 
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
        pk = kwargs["pk"]
        qs = self.get_queryset()
        instance = qs.filter(id=pk)
        if not instance.exists():
            return ResponseWrapper(error_msg="Product Stock records not found", error_code=404, status=404)
        serializer = self.get_serializer(instance.first())
        return ResponseWrapper(data = serializer.data, msg="Product Stock records Details")

    def destroy(self, request, **kwargs):
        qs = self.queryset.filter(**kwargs).first()
        if qs:
            qs.delete()
            return ResponseWrapper(status=200, msg='deleted')
        else:
            return ResponseWrapper(error_msg="Not Found", error_code=404, status=404)

class DiscountViewSet(CustomViewSet):
    serializer_class = DiscountSerializer
    pagination_class = CustomPagination
    queryset = Discount.objects.all()
    lookup_field = "pk"
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_fields = ("title",)
    filterset_class = DiscountFilter

    def get_serializer_class(self):
        if self.action == 'apply_discount_on_product':
            self.serializer_class = DiscountProductSerializer
        elif self.action == 'apply_discount_on_category_of_product':
            # self.serializer_class = RestaurantUpdateSerializer
            self.serializer_class = DiscountCategorySerializer

        else:
            self.serializer_class = DiscountSerializer

        return self.serializer_class

    # valid discount check method
    def valid_discount(self, discount):
        start_time = discount.start_time
        end_time = discount.end_time
        start_date = discount.start_date
        end_date = discount.end_date
        schedule_type = discount.schedule_type
        current_date = datetime.datetime.now().date()
        current_time = datetime.datetime.now().time()

        if schedule_type == "Time_Wise":
            if start_time <= current_time <= end_time:
                return True
            else:
                return False
        elif schedule_type == "Date_Wise":
            if start_date <= current_date <= end_date:
                return True
            else:
                return False




    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        qs = self.get_queryset()

        object = qs.filter(pk = pk)
        if not object.exists():
            return ResponseWrapper(error_msg="Discount not found", error_code=404, status=404)

        serializer = self.get_serializer(object.first())
        return ResponseWrapper(serializer.data)

    # def list(self, request, *args, **kwargs):
    #     queryset = self.filter_queryset(self.get_queryset())
    #
    #     page = self.paginate_queryset(queryset)
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)
    #
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        schedule_type = request.data.get('schedule_type')
        discount_type = request.data.get('discount_type')
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        amount = request.data.get('amount')

        title = request.data.get('title')
        title_already_exist = Discount.objects.filter(title__exact=title).last()

        if title_already_exist:
            return ResponseWrapper(error_msg='Discount with this title is already exist.', error_code=400, status=400)

        if int(amount) <=0:
            return ResponseWrapper(error_msg='Please enter a valid Amount for discount'
                                             ,error_code=400 , status = 400)

        if schedule_type == "Time_Wise":
            if start_time == "" or end_time == "":
                return ResponseWrapper(error_msg='start time and  end time fields are mandatory'
                                             ,error_code=400, status = 400)
            if start_time > end_time:
                return ResponseWrapper(error_msg='end time  must be later than start time'
                                             ,error_code=400, status = 400)
        if schedule_type == "Date_wise":
            if start_date == "" or end_date == "":
                return ResponseWrapper(error_msg='start date and  end date fields are mandatory'
                                            ,error_code=400, status = 400)
            if start_date > end_date:
                return ResponseWrapper(error_msg='end date  must be later than start date'
                                            ,error_code=400, status = 400)
       
        if discount_type == "PERCENTAGE":
            if int(amount) > 100:
                return ResponseWrapper(error_msg='Please enter discount amount equal or less than 100'
                                             ,error_code=400, status = 400)
        if serializer.is_valid():
            qs = serializer.save()
            return ResponseWrapper(data=serializer.data, msg='created', status=201)
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400, status=400)

    def update(self, request, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data,partial=True)

        discount_qs =  Discount.objects.filter(**kwargs).first()
        if not discount_qs:
            return ResponseWrapper(error_msg='Discount Not Found', error_code=404, status=404)

        title = request.data.get('title')
        if not title:
            title = discount_qs.title
        else:
            title=title

        title_already_exist = Discount.objects.filter(title__exact=title).exclude(id=discount_qs.id).last()

        if title_already_exist:
            return ResponseWrapper(error_msg='Discount with this title is already exist.', error_code=400, status=400)

        schedule_type = request.data.get('schedule_type')
        if schedule_type is None:
            schedule_type = discount_qs.schedule_type

        discount_type = request.data.get('discount_type')
        if discount_type is None:
            discount_type = discount_qs.discount_type

        start_time = request.data.get('start_time')
        if start_time is None:
            start_time = discount_qs.start_time

        end_time = request.data.get('end_time')
        if end_time is None:
            end_time = discount_qs.end_time

        start_date = request.data.get('start_date')
        if start_date is None:
            start_date = discount_qs.start_date

        end_date = request.data.get('end_date')
        if end_date is None:
            end_date = discount_qs.end_date

        amount = request.data.get('amount')
        if amount is None:
            amount = discount_qs.amount

        if int(amount) <= 0:
            return ResponseWrapper(error_msg='Please enter a valid Amount for discount'
                                            ,error_code=400 , status = 400)

        if schedule_type == "Time_Wise":
            if start_time == "" or end_time == "":
                return ResponseWrapper(error_msg='start time and  end time fields are mandatory'
                                             ,error_code=400, status = 400)
            if start_time > end_time:
                return ResponseWrapper(error_msg='end time  must be later than start time'
                                             ,error_code=400, status = 400)
        if schedule_type == "Date_wise":
            if start_date == "" or end_date == "":
                return ResponseWrapper(error_msg='start date and  end date fields are mandatory'
                                            ,error_code=400, status = 400)
            if start_date > end_date:
                return ResponseWrapper(error_msg='end date  must be later than start date'
                                            ,error_code=400, status = 400)

        if discount_type == "PERCENTAGE":
            if amount > 100:
                return ResponseWrapper(error_msg='Please enter discount amount equal or less than 100'
                                             ,error_code=400, status = 400)
        if serializer.is_valid():
            qs = serializer.update(instance=self.get_object(
            ), validated_data=serializer.validated_data)
            serializer = self.serializer_class(instance=qs)
            return ResponseWrapper(data=serializer.data)
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400, status=400)

    def valid_discount_list(self, request, *args, **kwargs):
        current_datetime = datetime.datetime.now(pytz.timezone("Asia/Dhaka"))
        current_date = current_datetime.date()
        current_time = current_datetime.time()
        qs = self.filter_queryset(self.get_queryset())

        filter_qs = []

        for discount in qs:
            valid_discount = self.valid_discount(discount)
            if valid_discount:
                filter_qs.append(discount)

        page_qs = self.paginate_queryset(filter_qs)
        serializer = DiscountSerializer(instance=page_qs, many=True)
        serializer = DiscountSerializer(instance=page_qs, many=True)
        paginated_data = self.get_paginated_response(serializer.data)

        return ResponseWrapper(
            data= paginated_data.data,
            status=200
        )

    def apply_discount_on_product(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data= request.data,partial=True)

        product_list = request.data.get("product")
        discount = request.data.get("discount")

        if not discount:
            return ResponseWrapper(error_msg="No Valid Discount is provided",
                error_code=400, status=400)

        if not product_list:
            return ResponseWrapper(error_msg="No Valid product list is provided",
                error_code=400, status=400)

        discount_qs = Discount.objects.filter(id=discount).first()
        if not discount_qs:
            return ResponseWrapper(error_msg="No Valid Discount id is provided",
                error_code=400, status=400)

        valid_discount = self.valid_discount(discount_qs)
        if not valid_discount:
            return ResponseWrapper(error_msg="Discount is not valid",
                error_code=400, status=400)

        # return ResponseWrapper("Discount is Successfully added to all products")

        if serializer.is_valid():
            for product in product_list:
                product_qs = Product.objects.filter(id=product).first()
                if not product_qs:
                    return ResponseWrapper(error_msg="No Valid Product id is provided",
                    error_code=400, status=400)
                product_qs.discount = discount_qs
                product_qs.save()

            product_qs = Product.objects.filter(id__in=product_list)

            page_qs = self.paginate_queryset(product_qs)
            serializer = CustomProductListSerializer(instance=page_qs, many=True)
            paginated_data = self.get_paginated_response(serializer.data)
            return ResponseWrapper(data=paginated_data.data,
                                   msg="Discount is successfully added to all products", status=200)

        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400, status=400)



    def apply_discount_on_category_of_product(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data= request.data,partial=True)

        category_id = request.data.get("category")
        discount = request.data.get("discount")

        if not discount:
            return ResponseWrapper(error_msg="No Valid Discount is provided",
                error_code=400, status=400)

        if not category_id:
            return ResponseWrapper(error_msg="No Valid Category id is provided",
                error_code=400, status=400)

        discount_qs = Discount.objects.filter(id=discount).first()
        if not discount_qs:
            return ResponseWrapper(error_msg="No Valid Discount id is provided",
                error_code=400, status=400)
        valid_discount = self.valid_discount(discount_qs)
        if not valid_discount:
            return ResponseWrapper(error_msg="This discount is not valid",
                error_code=400, status=400)

        product_list = Product.objects.filter(categories__id=category_id)

        if not product_list:
            return ResponseWrapper(error_msg="There is no product under this category",
                error_code=404, status=404)

        #return ResponseWrapper("Discount is successfully added to all products under the category")

        if serializer.is_valid():
            for product in product_list:
                product.discount = discount_qs
                product.save()

            product_qs = Product.objects.filter(categories__id=category_id)
            page_qs = self.paginate_queryset(product_qs)
            serializer = CustomProductListSerializer(instance=page_qs, many=True)
            paginated_data = self.get_paginated_response(serializer.data)
            return ResponseWrapper(data=paginated_data.data, msg="Discount is successfully added to all products under this category")

            # return ResponseWrapper(data=serializer.data, msg="Discount is successfully added to all products under this category")
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400, status=400)

    def destroy(self, request, **kwargs):
        qs = self.queryset.filter(**kwargs)
        if not qs.exists():
            return ResponseWrapper(error_msg="Discount not found", error_code=404, status=404)
        if qs:
            qs.first().delete()
            return ResponseWrapper(status=200, msg='deleted')
        else:
            return ResponseWrapper(error_msg="failed to delete", error_code=400, status=400)


class PromoCodeViewSet(CustomViewSet):
    serializer_class = PromoCodeSerializer
    pagination_class = CustomPagination
    queryset = PromoCode.objects.all()
    lookup_field = "pk"
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_fields = ("code",)
    filterset_class = PromoCodeFilter

    def get_serializer_class(self):
        if self.action == 'create':
            self.serializer_class = PromoCodeSerializer
        elif self.action == 'update':
            # self.serializer_class = RestaurantUpdateSerializer
            self.serializer_class = CustomPromoCodeSerializer

        else:
            self.serializer_class = PromoCodeSerializer

        return self.serializer_class

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        serializer_class = self.get_serializer_class()
        page_qs = self.paginate_queryset(qs)
        serializer = serializer_class(instance=page_qs, many=True, context={"request": request})
        paginated_data = self.get_paginated_response(serializer.data)
        return ResponseWrapper(data = paginated_data.data, msg='Success')

    def create(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        schedule_type = request.data.get('schedule_type')
        promo_type = request.data.get('promo_type')
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        amount = request.data.get('amount')
        minimum_purchase_amount = request.data.get('minimum_purchase_amount')
        max_purchase_amount = request.data.get('max_purchase_amount')
        maximum_applied = request.data.get('maximum_applied')

        code = request.data.get('code')
        code_already_exist = PromoCode.objects.filter(code__exact=code).last()

        if code_already_exist:
            return ResponseWrapper(error_msg='Promo code with this code already exists.', error_code=400, status=400)

        if float(maximum_applied) <= 0:
            return ResponseWrapper(error_msg='Maximum applied should be greater than 0', error_code=400, status = 400)

        if float(minimum_purchase_amount) <=0:
            return ResponseWrapper(error_msg='Minimum purchase amount should be greater than 0'
                                             , error_code=400, status = 400)

        if float(max_purchase_amount) <=0:
            return ResponseWrapper(error_msg='Maximum purchase amount should be greater than 0'
                                             , error_code=400, status = 400)

        if float(amount) <=0:
            return ResponseWrapper(error_msg='Please enter a valid Amount for discount'
                                             , error_code=400, status = 400)

        if float(minimum_purchase_amount) > float(max_purchase_amount):
            return ResponseWrapper(error_msg='Maximum purchase amount should be greater or equal to Minimum purchase amount'
                                             , error_code=400, status = 400)

        if schedule_type == "Time_Wise":
            if start_time == "" or end_time == "":
                return ResponseWrapper(error_msg='start time and  end time fields are mandatory'
                                             , error_code=400, status = 400)
            if start_time > end_time:
                return ResponseWrapper(error_msg='end time  must be later than start time'
                                             , error_code=400, status = 400)
        if schedule_type == "Date_wise":
            if start_date == "" or end_date == "":
                return ResponseWrapper(error_msg='start date and  end date fields are mandatory'
                                            , error_code=400, status = 400)
            if start_date > end_date:
                return ResponseWrapper(error_msg='end date  must be later than start date'
                                            , error_code=400, status = 400)

        if promo_type == "PERCENTAGE":
            if float(amount) > 100:
                return ResponseWrapper(error_msg='Please enter discount amount equal or less than 100'
                                             , error_code=400, status = 400)
        if serializer.is_valid():
            qs = serializer.save()
            return ResponseWrapper(data=serializer.data, msg='created', status=201)
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400, status=400)

    def update(self, request, **kwargs):
        serializer_class = CustomPromoCodeSerializer
        serializer = serializer_class(data=request.data, partial=True)

        qs = self.queryset.filter(**kwargs)
        if not qs.exists():
            return ResponseWrapper(error_msg="PromoCode not Found", error_code=404, status=404)

        PromoCode_object =  PromoCode.objects.filter(**kwargs).first()

        maximum_applied = request.data.get('maximum_applied')
        if maximum_applied is None:
            maximum_applied = PromoCode_object.maximum_applied

        schedule_type = request.data.get('schedule_type')
        if schedule_type is None:
            schedule_type = PromoCode_object.schedule_type

        promo_type = request.data.get('promo_type')
        if promo_type is None:
            promo_type = PromoCode_object.promo_type

        start_time = request.data.get('start_time')
        if start_time is None:
            start_time = PromoCode_object.start_time

        end_time = request.data.get('end_time')
        if end_time is None:
            end_time = PromoCode_object.end_time

        start_date = request.data.get('start_date')
        if start_date is None:
            start_date = PromoCode_object.start_date

        end_date = request.data.get('end_date')
        if end_date is None:
            end_date = PromoCode_object.end_date

        amount = request.data.get('amount')
        if amount is None:
            amount = PromoCode_object.amount

        minimum_purchase_amount = request.data.get('minimum_purchase_amount')
        if minimum_purchase_amount is None:
            minimum_purchase_amount = PromoCode_object.minimum_purchase_amount

        max_purchase_amount = request.data.get('max_purchase_amount')
        if max_purchase_amount is None:
            max_purchase_amount = PromoCode_object.max_purchase_amount

        if float(maximum_applied) <= 0:
            return ResponseWrapper(error_msg='Maximum applied should be greater than 0', error_code=400, status = 400)

        if float(minimum_purchase_amount) <=0:
            return ResponseWrapper(error_msg='Minimum purchase amount should be greater than 0',
                                            error_code=400 , status = 400)

        if float(max_purchase_amount) <=0:
            return ResponseWrapper(error_msg='Maximum purchase amount should be greater than 0'
                                             , error_code=400, status = 400)

        if float(amount) <=0:
            return ResponseWrapper(error_msg='Please enter a valid Amount for discount'
                                             , error_code=400, status = 400)

        if float(minimum_purchase_amount) > float(max_purchase_amount):
            return ResponseWrapper(error_msg='Maximum purchase amount should be greater or equal to Minimum purchase amount'
                                             , error_code=400, status = 400)

        if schedule_type == "Time_Wise":
            if start_time == "" or end_time == "":
                return ResponseWrapper(error_msg='start time and  end time fields are mandatory'
                                             , error_code=400, status = 400)
            if start_time > end_time:
                return ResponseWrapper(error_msg='end time  must be later than start time'
                                             , error_code=400, status = 400)
        if schedule_type == "Date_wise":
            if start_date == "" or end_date == "":
                return ResponseWrapper(error_msg='start date and  end date fields are mandatory'
                                            , error_code=400, status = 400)
            if start_date > end_date:
                return ResponseWrapper(error_msg='end date  must be later than start date'
                                            , error_code=400, status = 400)

        if promo_type == "PERCENTAGE":
            if float(amount) > 100:
                return ResponseWrapper(error_msg='Please enter a discount amount equal or less than 100'
                                             , error_code=400, status = 400)
        if serializer.is_valid():
            qs = serializer.update(instance=self.get_object(
            ), validated_data=serializer.validated_data)
            serializer = self.serializer_class(instance=qs)
            return ResponseWrapper(data=serializer.data)
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400, status=400)

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        qs = self.get_queryset()

        object = qs.filter(pk = pk)
        if not object.exists():
            return ResponseWrapper(error_msg="Promocode not found", error_code=404, status=404)

        serializer = self.get_serializer(object.first())
        return ResponseWrapper(serializer.data)

    def destroy(self, request, **kwargs):
        qs = self.queryset.filter(**kwargs)
        if not qs.exists():
            return ResponseWrapper(error_msg="Promocode not found", error_code=404, status=404)
        if qs:
            qs.first().delete()
            return ResponseWrapper(status=200, msg='deleted')
        else:
            return ResponseWrapper(error_msg="failed to delete", error_code=400, status=400)




# class DiscountProductView(viewsets.ModelViewSet):
#     serializer_class = DiscountProductSerializer
#     # permission_classes = [IsDepoManager]
#     queryset = Product.objects.all()
#     lookup_field = "pk"
# class DiscountCategoryView(viewsets.ModelViewSet):
#     serializer_class = DiscountCategorySerializer
#     # permission_classes = [IsDepoManager]
#     queryset = Category.objects.all()
#     lookup_field = "pk"
    def valid_promo_code_list(self, request, *args, **kwargs):
        current_datetime = datetime.datetime.now(pytz.timezone("Asia/Dhaka"))
        current_date = current_datetime.date()
        current_time = current_datetime.time()

        qs = self.filter_queryset(self.get_queryset())

        filter_qs = []

        for promo in qs:
            start_time = promo.start_time
            end_time = promo.end_time
            start_date = promo.start_date
            end_date = promo.end_date
            # max_purchase_amount = promo.max_purchase_amount
            # min_purchase_amount = promo.minimum_purchase_amount
            # max_applied = promo.maximum_applied

            # check date
            if promo.schedule_type == 'Date_Wise':
                if start_date and end_date:
                    if end_date >= current_date >= start_date:
                        filter_qs.append(promo)

            # check time
            else:
                if start_time and end_time:
                    if end_time >= current_time >= start_time:
                        filter_qs.append(promo)

        page_qs = self.paginate_queryset(filter_qs)
        serializer = PromoCodeSerializer(instance=page_qs, many=True)
        paginated_data = self.get_paginated_response(serializer.data)

        return ResponseWrapper(
            data=paginated_data.data,
            status=200
        )


class DiscountProductView(viewsets.ModelViewSet):
    serializer_class = DiscountProductSerializer
    # permission_classes = [IsDepoManager]
    queryset = Product.objects.all()
    lookup_field = "pk"

class DiscountCatagoryView(viewsets.ModelViewSet):
    serializer_class = DiscountCategorySerializer
    # permission_classes = [IsDepoManager]
    queryset = Category.objects.all()
    lookup_field = "pk"