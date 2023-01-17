from customapp.models import Version, CustomerAddress
from customapp.serializers import *
from utils import custom_viewset
from rest_framework.permissions import IsAuthenticated, AllowAny
from utils.response_wrapper import ResponseWrapper
from rest_framework import generics
from oscar.core.loading import get_class, get_model
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import parser_classes
from accounts.models import UserAccount as User
from django.db.models import Q
from utils.custom_viewset import CustomViewSet
#from oscar.apps.address.models import UserAddress
from oscar.apps.order.models import ShippingAddress, BillingAddress
from oscar.apps.address.models import Country
from apps.partner.models import Partner
import re
from django.db.models import Q
from utils.custom_viewset import CustomViewSet
from django.db import IntegrityError
from apps.order.models import Order
from apps.catalogue.models import Product
from apps.partner.models import Partner
from oscar.apps.order.models import Line
from apps.partner.models import PartnerType

ProductImage = get_model('catalogue', 'ProductImage')
# Product = get_model('catalogue', 'Product')
StockRecord = get_model('partner', 'StockRecord')
# # Partner = get_model('partner', 'Partner')
# ProductReview = get_model('reviews', 'ProductReview')


# Create CRUD API for Version model
class VersionViewSet(CustomViewSet):
    queryset = Version.objects.all()
    serializer_class = VersionSerializer
    # permission_classes = (IsAuthenticated,)

    # def get_queryset(self):
    #     return super().get_queryset()

    # def list(self, request, *args, **kwargs):
    #     return super().list(request, *args, **kwargs)

    def latest_version(self, request, *args, **kwargs):
        qs = Version.objects.all().order_by('version').last()
        if not qs:
            return ResponseWrapper(error_code=400, error_msg='Version Not Found', status = 400)
        serializer = VersionSerializer(instance=qs)
        return ResponseWrapper(data=serializer.data, status=200, msg='Success')

    def create(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        version = request.data.get('version')
        download_url = request.data.get('download_url')
        version_qs = Version.objects.filter(version = version)

        regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if not (re.match(regex, download_url) is not None):
            return ResponseWrapper(error_code=400, error_msg='Download URL is not in valid Format. Example: "https://www.google.com/" ', status=400)

        if version_qs:
            return ResponseWrapper(error_code=400,  error_msg='Version is Already Found', status=400)

        serializer = serializer_class(data=request.data)
        if serializer.is_valid():
            qs = serializer.save()
            return ResponseWrapper(data=serializer.data, msg='created', status=200)
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400, status=400)
    def update(self, request, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, partial=True)
        
        version = request.data.get('version')
        if version:
            if Version.objects.filter(version__iexact=version).exclude(**kwargs).exists():
                return ResponseWrapper(error_msg="There is another Entry with same version", error_code=400, status = 400)
        
        regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        download_url = request.data.get('download_url')
        if download_url:
            if not (re.match(regex, download_url) is not None):
                return ResponseWrapper(error_code=400, error_msg='Download URL is not in valid Format. Example: "https://www.google.com/" ', status=400)

        if serializer.is_valid():
            qs = serializer.update(instance=self.get_object(
            ), validated_data=serializer.validated_data)
            serializer = self.serializer_class(instance=qs)
            return ResponseWrapper(data=serializer.data, status = 200)
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400, status=400)
    

# class VersionSpecificViewSet(CustomViewSet):
#     queryset = Version.objects.all()
#     serializer_class = VersionSpecificSerializer
#     permission_classes = (IsAuthenticated,)
#     lookup_field = 'pk'
    

#     def get_queryset(self):
#         return super().get_queryset()

#     def get(self, request, *args, **kwargs):
#         return super().retrieve(request, *args, **kwargs)

#     def update(self, request, *args, **kwargs):
#         return super().update(request, *args, **kwargs)


# class VersionLatestViewSet(CustomViewSet):
#     queryset = Version.objects.all()
#     serializer_class = VersionSerializer
#     permission_classes = (IsAuthenticated,)
    

#     def get_queryset(self):
#         return super().get_queryset().order_by('-id').first()

#     def get(self, request, *args, **kwargs):
#         return ResponseWrapper(
#             self.serializer_class(self.get_queryset()).data
#         )



# CRUD API for ProductImage model
class CustomProductImageViewSet(CustomViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = CustomProductImageSerializer
    lookup_field = "pk"

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        serializer_class = self.get_serializer_class()
        page_qs = self.paginate_queryset(qs)
        serializer = serializer_class(instance=page_qs, many=True)
        paginated_data = self.get_paginated_response(serializer.data)
        return ResponseWrapper(data=paginated_data.data, msg="Success")

    def create(self, request, product_id, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        product_qs = Product.objects.filter(id=product_id).last()
        if not product_qs:
            return ResponseWrapper(error_msg='Product is not found', error_code=404, status=404)
        data_item = request.data
        for item in data_item:
            item["product"] = product_qs.id

        serializer = serializer_class(data=data_item, many = True)

        if serializer.is_valid():
            for item in serializer.data:
                item['product'] = product_qs.id
            qs = serializer.save()
            serializer = serializer_class(data=qs, many = True)
            return ResponseWrapper(data=serializer.data, msg='created', status=201)
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400, status=400)

    def update(self, request, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, partial=True)

        qs = self.queryset.filter(**kwargs)
        if not qs.exists():
            return ResponseWrapper(
                error_msg="Product Image Not Found", 
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
            return ResponseWrapper(error_msg="Product Image not found", error_code=404, status=404)
        serializer = self.get_serializer(instance.first())
        return ResponseWrapper(data = serializer.data, msg="Product Image Details")

    def destroy(self, request, **kwargs):
        qs = self.queryset.filter(**kwargs).first()
        if qs:
            qs.delete()
            return ResponseWrapper(status=200, msg='deleted')
        else:
            return ResponseWrapper(error_msg='Product Image Not Found', error_code=404, status=404)


# CRUD API for StockRecord model
class StockRecordListView(generics.ListCreateAPIView):
    queryset = StockRecord.objects.all()
    serializer_class = StockRecordSerializerCustom

    def get_queryset(self):
        return super().get_queryset().filter(product=self.kwargs['pk'], partner=self.kwargs['partner'])

    def get(self, request, *args, **kwargs):
        return ResponseWrapper(
            self.serializer_class(self.get_queryset(), many=True).data , status=200
        )

    def create(self, request, *args, **kwargs):
        product = Product.objects.filter(pk=self.kwargs['pk']).first()
        partner = Partner.objects.filter(pk=self.kwargs['partner']).first()
        stock_record = StockRecord.objects.create(product=product, partner=partner, price_excl_tax=request.data['price_excl_tax'])
        return ResponseWrapper(
            self.serializer_class(stock_record).data, status=200
        )


class StockRecordSpecificView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StockRecord.objects.all()
    serializer_class = StockRecordSerializerCustom
    lookup_field = 'pk'

    def get_queryset(self, **kwargs):
        return super().get_queryset().filter(product=self.kwargs['pk'], partner=self.kwargs['partner'])

    def get(self, request, *args, **kwargs):
        return ResponseWrapper(
            self.serializer_class(self.get_queryset().get(pk=self.kwargs['pk'])).data, status=200
        )

    def update(self, request, *args, **kwargs):
        stock_record = self.get_queryset().get(pk=self.kwargs['pk'])
        stock_record.price_excl_tax = request.data['price_excl_tax']
        stock_record.save()
        return ResponseWrapper(
            self.serializer_class(stock_record).data, status=200
        )

    def destroy(self, request, *args, **kwargs):
        stock_record = self.get_queryset().get(pk=self.kwargs['pk'])
        stock_record.delete()
        return ResponseWrapper(
            self.serializer_class(stock_record).data, status=200,msg="Deleted"
        )

# CRUD API for Product Review model
class ProductReviewListView(CustomViewSet):
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializerCustom


    # permission_classes = (IsAuthenticated,)

    def get_permissions(self):
        if self.action == "review_update":
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return super().get_queryset().filter(product=self.kwargs['pk'])

    def review_update(self, request,pk, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, partial=True)
        qs = ProductReview.objects.filter(pk = pk).last()
        if not qs:
            return ResponseWrapper(error_msg='Review Not Found', error_code=404, status = 404)

        score = request.data['score']

        if score > 5:
            return ResponseWrapper(
                error_msg="Score has to be within 0 to 5", error_code=400, status=400
            )

        if serializer.is_valid():
            qs = serializer.update(instance=self.get_object(
            ), validated_data=serializer.validated_data)
            serializer = self.serializer_class(instance=qs)
            return ResponseWrapper(data=serializer.data, status=200)
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400, status=400)


    def list(self, request,product_id, *args, **kwargs):
        qs = ProductReview.objects.filter(product_id = product_id)
        serializer = self.serializer_class(instance=qs, many=True)
        return ResponseWrapper(data=serializer.data, msg='Success', status=200)


    def create(self, request,product_id, *args, **kwargs):
        product = Product.objects.filter(pk=product_id).last()
        user_qs = User.objects.filter(Q(email__exact=request.user) | Q(phone__exact=request.user)).last()
        check_qs = ProductReview.objects.filter(product=product, user_id=user_qs.id).last()
        score = request.data['score']

        # Check if user has placed an order for the product and the order is delivered
        line_qs = Line.objects.filter(product=product, order__user=user_qs)
        order_qs = Order.objects.filter(user=user_qs, lines__in=line_qs, status='Delivered').last()

        if not order_qs:
            return ResponseWrapper(
            error_msg="You have to place an order for this product before you can review it", error_code=400,status=400
            )

        if score > 5:
            return ResponseWrapper(
            error_msg="Score has to be within 0 to 5", error_code=400,status=400
             )
            
        if check_qs:
            return ResponseWrapper(
            error_msg="You already a Review for this product", error_code=400,status=400
             )

        product_review = ProductReview.objects.create(product=product, user_id=user_qs.id,
                                                      title=request.data['title'], score=score,
                                                      body=request.data['body'])
        product_review.total_votes += 1
        return ResponseWrapper(
            self.serializer_class(product_review).data, status=200
        )

class ProductReviewSpecificView(CustomViewSet):
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializerCustom
    lookup_field = 'pk'
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        qs = self.get_queryset()
        object = qs.filter(pk = pk)
        if not object.exists():
            return ResponseWrapper(error_msg="There is no review for with id", error_code=404, status=404)

        serializer = self.get_serializer(object.first())
        return ResponseWrapper(serializer.data)

    def update(self, request, **kwargs):
        pk = kwargs.get("pk")
        qs = self.get_queryset()
        object = qs.filter(pk = pk)
        if not object.exists():
            return ResponseWrapper(error_msg="There is no review for with id", error_code=404, status=404)
  
        score = request.data.get('score')
        if score:
            if float(score) > 5:
                return ResponseWrapper(
                error_msg="Score has to be within 0 to 5", error_code=400,status=400
                )

        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, partial=True)
        if serializer.is_valid():
            qs = serializer.update(instance=self.get_object(
            ), validated_data=serializer.validated_data)
            serializer = self.serializer_class(instance=qs)
            return ResponseWrapper(data=serializer.data, msg='updated', status=200)
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400, status=400)



class UserAddressView(CustomViewSet):
    queryset = CustomerAddress.objects.all()
    serializer_class = CustomUserAddressSerializer
    lookup_field = 'pk'
    permission_classes = (IsAuthenticated,)

    def customer_address_list(self, request, *args, **kwargs):
        qs = CustomerAddress.objects.filter(user = request.user)
        serializer_class = self.get_serializer_class()
        page_qs = self.paginate_queryset(qs)
        serializer = serializer_class(instance=page_qs, many=True)
        paginated_data = self.get_paginated_response(serializer.data)
        return ResponseWrapper(data=paginated_data.data, msg="Success", status=200)
        return ResponseWrapper(data=paginated_data.data, msg="Success",status=200)

        # serializer = serializer_class(instance = qs, many = True)
        # return ResponseWrapper(data = serializer.data, msg='Success')

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        qs = self.get_queryset()

        object = qs.filter(pk = pk)
        if not object.exists():
            return ResponseWrapper(error_msg="User Address not found", error_code=404,status=404)

        serializer = self.get_serializer(object.first())
        return ResponseWrapper(serializer.data,status=200)

    def destroy(self, request, **kwargs):
        qs = self.queryset.filter(**kwargs).first()
        if qs:
            qs.delete()
            return ResponseWrapper(status=200, msg='deleted')
        else:
            return ResponseWrapper(error_msg="failed to delete", error_code=404,status=404)

    def update(self, request,pk, **kwargs):
        qs = CustomerAddress.objects.filter(id = pk).last()
        if qs and qs.user == request.user:
            serializer_class = self.get_serializer_class()
            serializer = serializer_class(data=request.data, partial=True)

            if serializer.is_valid():
                try:
                    qs = serializer.update(instance=self.get_object(
                    ), validated_data=serializer.validated_data)
                    serializer = self.serializer_class(instance=qs)
                    return ResponseWrapper(data=serializer.data)
                except IntegrityError:
                    return ResponseWrapper(
                        error_msg="User address with this information is already exists.", 
                        error_code=400,
                        status=400
                    )
                except Exception as e:
                    return ResponseWrapper(
                        error_msg="Failed", 
                        error_code=400,
                        status=400
                    )
            else:
                return ResponseWrapper(
                    error_msg=serializer.errors,
                    error_code=400,
                    status=400
                )
        else:
            return ResponseWrapper(
                error_msg="User Address not found",
                error_code=404,
                status=404
            )

    def create(self, request, *args, **kwargs):
        try:
            user = User.objects.filter(id=request.user.id).last()
            if not user:
                return ResponseWrapper(
                    error_msg="Only Users can create a Address associated with account",
                    error_code=400,
                    status=400
                )

            is_daily_needs = request.data.get('is_daily_needs')
            is_marketplace = request.data.get('is_marketplace')
            is_services = request.data.get('is_services')
            is_for_all = request.data.get('is_for_all')

            serializer_class = self.get_serializer_class()
            serializer = serializer_class(data=request.data)

            if serializer.is_valid():
                first_name = serializer.validated_data.get('first_name')
                last_name = serializer.validated_data.get('last_name')
                state = serializer.validated_data.get('city')
                country = 'Bangladesh'
                phone_number = serializer.validated_data.get('phone_number')
                line1 = serializer.validated_data.get('address')
                line2 = serializer.validated_data.get('house_street_road')

                if country:
                    country = Country.objects.filter(name=country).last()
                    if not country:
                        return ResponseWrapper(
                            error_msg="The provided country name is not Valid",
                            error_code=400, 
                            status=404
                        )
                
                shipping_address = ShippingAddress.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    line1=line1,
                    line2=line2,
                    line4=state,
                    state=state,
                    country=country,
                    phone_number=phone_number,
                )
                billing_address = BillingAddress.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    line1=line1,
                    line2=line2,
                    line4=state,
                    state=state,
                    country=country,
                )
                    

                user_address = CustomerAddress.objects.create(
                    user=user,
                    first_name=first_name,
                    last_name=last_name,
                    line1=line1,
                    line2=line2,
                    line4=state,
                    country=country,
                    is_default_for_shipping=True,
                    is_default_for_billing=True,
                    phone_number=phone_number,
                )

                if is_daily_needs:
                    partner_type = PartnerType.objects.filter(name='Daily Needs').last()
                    if partner_type:
                        user_address.partner_type.add(partner_type)
                if is_marketplace:
                    partner_type = PartnerType.objects.filter(name='Marketplace').last()
                    if partner_type:
                        user_address.partner_type.add(partner_type)
                if is_services:
                    partner_type = PartnerType.objects.filter(name='Service').last()
                    if partner_type:
                        user_address.partner_type.add(partner_type)
                if is_for_all:
                    partner_type = PartnerType.objects.all()
                    for partner in partner_type:
                        user_address.partner_type.add(partner)
                        
                user_address.address = user_address.line1
                if user_address.line2:
                    user_address.house_street_road = user_address.line2

                serializer = CustomUserAddressSerializer(
                    instance=user_address
                )
                return ResponseWrapper(
                    data=serializer.data,
                    msg="Address Created Successfully",
                    status=200
                )
            else:
                return ResponseWrapper(error_msg=serializer.errors, error_code=400,status=400)
        except Exception as e:
            print(e)
            return ResponseWrapper(
                error_msg="Try with different value",
                error_code=400,
                status=400
            )

class ShippingAddressSpecificListView(CustomViewSet):
    queryset = ShippingAddress.objects.all()
    serializer_class = ShippingAddressSerializerCustom
    lookup_field = 'pk'
    permission_classes = (IsAuthenticated,)


class BillingAddressSpecificListView(CustomViewSet):
    queryset = BillingAddress.objects.all()
    serializer_class = BillingAddressSerializerCustom
    lookup_field = 'pk'
    permission_classes = (IsAuthenticated,)


class UserProductReviewListView(CustomViewSet):
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializerCustom
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        return ResponseWrapper(
            self.serializer_class(self.get_queryset(), many=True).data, status=200
        )