from oscar.apps.wishlists.models import *  # noqa isort:skip
from rest_framework import viewsets
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from utils.custom_viewset import CustomViewSet
from .serializers import WishlistSerializer, WishlistCreateSerializer
from apps.catalogue.models import Product
from utils.response_wrapper import ResponseWrapper
from utils.custom_pagination import CustomPagination
from apps.catalogue.serializers import CustomProductSerializer,CustomProductWishlistSerializer, CustomProductListSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import viewsets, serializers, filters
from django_filters.rest_framework import DjangoFilterBackend
from .filters import *
# class WishlistViewSet(CustomViewSet):
#     queryset = WishList.objects.all()
#     serializer_class = WishlistSerializer
#     lookup_field = 'pk'

#     def create(self, request, *args, **kwargs):
#         serializer_class = WishlistCreateSerializer
#         serializer = serializer_class(data=request.data)

#         if serializer.is_valid():
#             product_id = serializer.validated_data.get('product_id')

#             # creating wishlist
#             # wishlist = WishList.objects.create(owner=request.user)
#             wishlist, created = WishList.objects.update_or_create(owner=request.user)
#             product = get_object_or_404(Product, id=product_id)
#             wishlist.add(product)
#             wishlist.save()

#             serializer_create = WishlistSerializer(wishlist)
#             return Response(data = serializer_create.data)
#         else:
#             return Response(serializer.errors, status=400)


class WishlistViewSet(CustomViewSet):
    queryset = WishList.objects.all()
    serializer_class = WishlistCreateSerializer
    pagination_class = CustomPagination
    serializer_class_list = WishlistSerializer
    # permission_classes = IsAuthenticated
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_fields = ("owner", "key")
    filterset_class = WishListFilter 

    def get_permissions(self):
        if self.action == "customer_wishlist_remove":
            permission_classes = [IsAuthenticated]
        elif self.action == "customer_wishlist":
            permission_classes = [IsAuthenticated]
        elif self.action == "create":
            permission_classes = [IsAuthenticated]
        elif self.action == "customer_wishlist":
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = WishList.objects.filter(owner=self.request.user)
        return queryset

    def customer_wishlist_remove(self, request, *args, **kwargs):
        try:
            product_id = request.data.get('product_id')
            if product_id is not None:
                qs = WishList.objects.filter(lines__product__id = product_id).last()
                if not qs:
                    return ResponseWrapper(error_msg='Wish List Not Found',status=400, error_code=400)
                product_qs = qs.lines.filter(product__id = product_id)
                product_qs.delete()
                return ResponseWrapper(msg='Remove Successfully', status=200)
            else:
                return ResponseWrapper(
                    error_msg='Product id is Required', error_code=400,status=400
                )
        except Exception as e:
            return ResponseWrapper(
                error_code=404, status=404,error_msg='Failed'
            )

    def customer_wishlist(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return ResponseWrapper(
                error_code=200, status=200,error_msg='No Wishlist Found'
            )
        serializer = WishlistSerializer(queryset, many=True)
        marketplace_product_list = []
        dailyneeds_product_list = []
        service_product_list = []
        for wishlist in serializer.data:
            for product in wishlist['product_list']:

                product_qs = Product.objects.filter(id=product['product']['id']).first()
                categories = product_qs.categories.first().partner_type.name

                if categories == 'Marketplace':
                    marketplace_product_list.append(product_qs)

                if categories == 'Daily Needs':
                    dailyneeds_product_list.append(product_qs)

                if categories == 'Service':
                    service_product_list.append(product_qs)

        # marketplace_product_serializer = CustomProductSerializer(instance=self.paginate_queryset(marketplace_product_list), many=True, context={'request': request}).data
        # dailyneeds_product_serializer = CustomProductSerializer(instance=self.paginate_queryset(dailyneeds_product_list), many=True, context={'request': request}).data
        # service_product_serializer = CustomProductSerializer(instance=self.paginate_queryset(service_product_list), many=True, context={'request': request}).data
        marketplace_page_qs = self.paginate_queryset(marketplace_product_list)
        dailyneeds_page_qs = self.paginate_queryset(dailyneeds_product_list)
        service_page_qs = self.paginate_queryset(service_product_list)

        paginated_marketplace_product_serializer = CustomProductSerializer(instance=marketplace_page_qs, many=True,
                                                                           context={"request": request})
        paginated_dailyneeds_product_serializer = CustomProductListSerializer(instance=dailyneeds_page_qs, many=True,
                                                                           context={"request": request})
        paginated_service_product_serializer = CustomProductListSerializer(instance=service_page_qs, many=True,
                                                                           context={"request": request})
        data = {
            'marketplace_product_list': paginated_marketplace_product_serializer.data,
            'dailyneeds_product_list': paginated_dailyneeds_product_serializer.data,
            'service_product_list': paginated_service_product_serializer.data
        }
        return ResponseWrapper(
            data=data,
            msg='Success',
            status=200
        )


    def create(self, request, *args, **kwargs):
        try:
            # product_ids = request.data.get('product_ids')
            product_id = request.data.get('product_id')
        
            if product_id :
                product_qs = Product.objects.filter(id = product_id).last()
                if not product_qs:
                    return ResponseWrapper(error_code=404, status=404, error_msg='Product Not Found')

                # creating wishlist
                # wishlist = WishList.objects.create(owner=request.user)
                wishlist, created = WishList.objects.update_or_create(owner=request.user)
                product = get_object_or_404(Product, id=product_id)
                wishlist.add(product)
                wishlist.save()

                serializer_create = CustomProductListSerializer(product_qs)
                return ResponseWrapper(data = serializer_create.data, status=201, msg='Success')
            else:
                return ResponseWrapper(
                    error_msg='Product id is Required', error_code=400,status=400
                )
        except Exception as e:
            return ResponseWrapper(
                error_code=404, status=404,error_msg='Failed'
            )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = WishlistSerializer(queryset, many=True)
        wishlist_data = serializer.data
        product_list = {'marketPlace':[],'service':[],'dailyNeeds':[]}
        try:
            for wishlist in wishlist_data:
                for product in wishlist['product_list']:
                    product_qs = Product.objects.filter(id=product['id']).last()
                    try:
                        if product_qs.zone.partners.last().partner_type.name == 'Marketplace':
                            product_list['marketPlace'].append(product)
                        elif product_qs.zone.partners.last().partner_type.name == 'Service':
                            product_list['service'].append(product)
                        elif product_qs.zone.partners.last().partner_type.name == 'Daily Needs':
                            product_list['dailyNeeds'].append(product)
                    except:
                        pass
            wishlist_data[0]['product_list'] = product_list

# class WishlistUserViewSet(CustomViewSet):
#     queryset = WishList.objects.all()
#     serializer_class = WishlistSerializer

#     def get_queryset(self):
#         queryset = WishList.objects.filter(owner=self.request.user)
#         return queryset

#     def list(self, request, *args, **kwargs):
#         queryset = self.get_queryset()
#         serializer = self.get_serializer(queryset, many=True)
#         wishlist_data = serializer.data
#         product_list = {'marketPlace':[],'service':[],'dailyNeeds':[]}
#         try:
#             for wishlist in wishlist_data:
#                 for product in wishlist['product_list']:
#                     product_qs = Product.objects.filter(id=product['id']).last()
#                     try:
#                         if product_qs.zone.partners.last().partner_type.name == 'Marketplace':
#                             product_list['marketPlace'].append(product)
#                         elif product_qs.zone.partners.last().partner_type.name == 'Service':
#                             product_list['service'].append(product)
#                         elif product_qs.zone.partners.last().partner_type.name == 'Daily Needs':
#                             product_list['dailyNeeds'].append(product)
#                     except:
#                         pass
#             wishlist_data[0]['product_list'] = product_list

            return ResponseWrapper(
                data=wishlist_data,
            )
        except Exception as e:
            return ResponseWrapper(
                error_msg=str(e),
            )

    def customer_list(self, request, *args, **kwargs):
        wishlist_qs = WishList.objects.filter(owner = request.user).first()
        marketplace_product_list = []
        dailyneeds_product_list = []
        service_product_list = []

        for product in wishlist_qs.lines.all():
            qs = product.product.categories.first().partner_type.name
            if qs == 'Marketplace':
                marketplace_product_list.append(product)
            elif qs == 'Daily Needs':
                dailyneeds_product_list.append(product)
            else:
                service_product_list.append(product)

        page_qs = self.paginate_queryset(marketplace_product_list)
        serializer = CustomProductWishlistSerializer(instance=page_qs, many=True)
        paginated_data = self.get_paginated_response(serializer.data)
        return ResponseWrapper(
            data={
                'marketplace_product_list': paginated_data.data
            },
            status=200
        )


class WishlistUserViewSet(CustomViewSet):
    queryset = WishList.objects.all()
    serializer_class = WishlistSerializer

    def get_queryset(self):
        queryset = WishList.objects.filter(owner=self.request.user)
        return queryset

