import uuid
from django.shortcuts import render, get_object_or_404
from oscarapi.views.product import ProductSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from django.db import transaction
from apps.catalogue.models import Category, Product
from utils.custom_viewset import CustomViewSet
from utils.response_wrapper import ResponseWrapper
from apps.order.models import *
from oscarapi.serializers.checkout import Country

from .models import *
from .serializers import *
from .filters import *
from apps.catalogue.serializers import *
import random
from rest_framework import filters, permissions, status, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from apps.partner.models import *
from rest_framework.request import Request
from drf_yasg2.utils import swagger_auto_schema
from drf_yasg2 import openapi
from utils.custom_pagination import *
from oscar.apps.catalogue.categories import create_from_sequence

# from sit


# Create your views here.
class HomePageViewSet(CustomViewSet):
    # serializer_class = HomePageDetailsSerializer
    serializer_class = CustomProductSerializer
    pagination_class = CustomPagination
    queryset = None
    # filterset_class = HomePageFilter
    # filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    # filterset_fields = ("id","upc","title","rating","categories")

    def top_recommended_market_place_product_list(self, request, *args, **kwargs):
        top_recommended_market_place_qs = self.filter_queryset(
            Product.objects.filter(
                is_public=True, categories__partner_type__name="Marketplace"
            )
            .exclude(structure="CHILD")
            .distinct()
        )

        # serializer = CustomProductListSerializer(instance=top_recommended_market_place_qs, many=True,context={"request": request},)
        #
        # return ResponseWrapper(
        #     data= serializer.data,
        #     status=200
        # )
        page_qs = self.paginate_queryset(top_recommended_market_place_qs)
        serializer = CustomProductListSerializer(instance=page_qs, many=True, context={"request": request},)
        paginated_data = self.get_paginated_response(serializer.data)
        return ResponseWrapper(data=paginated_data.data, msg="Success")

    def market_place_trending_product_list(self, request, *args, **kwargs):
        product_type_qs = PartnerType.objects.filter(name__icontains="market").last()
        trending_product_qs = self.filter_queryset(
            Product.objects.filter(
                categories__partner_type=product_type_qs, is_public=True
            )
            .exclude(structure="CHILD")
            .distinct()
        )

        # serializer = CustomProductListSerializer(instance=trending_product_qs, many=True,context={"request": request},)
        #
        # return ResponseWrapper(
        #     data= serializer.data,
        #     status=200
        # )
        page_qs = self.paginate_queryset(trending_product_qs)
        serializer = CustomProductListSerializer(instance=page_qs, many=True, context={"request": request}, )
        paginated_data = self.get_paginated_response(serializer.data)
        return ResponseWrapper(data=paginated_data.data, msg="Success")

    def market_place_best_selling_product_list(self, request, *args, **kwargs):
        product_type_qs = PartnerType.objects.filter(name__icontains="market").last()
        best_selling_product_qs = self.filter_queryset(
            Product.objects.filter(
                categories__partner_type=product_type_qs, is_public=True
            )
            .exclude(structure="CHILD")
            .distinct()
        )

        # serializer = CustomProductListSerializer(instance=best_selling_product_qs, many=True,context={"request": request},)
        #
        # return ResponseWrapper(
        #     data= serializer.data,
        #     status=200
        # )
        page_qs = self.paginate_queryset(best_selling_product_qs)
        serializer = CustomProductListSerializer(instance=page_qs, many=True, context={"request": request}, )
        paginated_data = self.get_paginated_response(serializer.data)
        return ResponseWrapper(data=paginated_data.data, msg="Success")

    def market_place_lowest_price_product_list(self, request, *args, **kwargs):
        product_type_qs = PartnerType.objects.filter(name__icontains="market").last()
        lowest_price_product_qs = self.filter_queryset(
            Product.objects.filter(
                categories__partner_type=product_type_qs, is_public=True
            )
            .exclude(structure="CHILD")
            .order_by("stockrecords__price")
            .distinct()
        )

        # serializer = CustomProductListSerializer(instance=lowest_price_product_qs, many=True,context={"request": request},)
        #
        # return ResponseWrapper(
        #     data= serializer.data,
        #     status=200
        # )
        page_qs = self.paginate_queryset(lowest_price_product_qs)
        serializer = CustomProductListSerializer(instance=page_qs, many=True, context={"request": request}, )
        paginated_data = self.get_paginated_response(serializer.data)
        return ResponseWrapper(data=paginated_data.data, msg="Success")

    def market_place_featured_product_list(self, request, *args, **kwargs):
        product_type_qs = PartnerType.objects.filter(name__icontains="market").last()
        featured_product_qs = self.filter_queryset(
            Product.objects.filter(
                categories__partner_type=product_type_qs, is_public=True
            )
            .exclude(structure="CHILD")
            .distinct()
        )

        # serializer = CustomProductListSerializer(instance=featured_product_qs, many=True,context={"request": request},)
        #
        # return ResponseWrapper(
        #     data= serializer.data,
        #     status=200
        # )
        page_qs = self.paginate_queryset(featured_product_qs)
        serializer = CustomProductListSerializer(instance=page_qs, many=True, context={"request": request}, )
        paginated_data = self.get_paginated_response(serializer.data)
        return ResponseWrapper(data=paginated_data.data, msg="Success")

    def market_place_best_seller_list(self, request, *args, **kwargs):
        self.filterset_class = PartnerFilter
        best_seller_qs = self.filter_queryset(
            Partner.objects.filter(
                partner_type__name='Marketplace'
            )
        )

        # serializer = PartnerSerializer(instance=best_seller_qs, many=True,context={"request": request},)
        #
        # return ResponseWrapper(
        #     data= serializer.data,
        #     status=200
        # )
        page_qs = self.paginate_queryset(best_seller_qs)
        serializer = PartnerSerializer(instance=page_qs, many=True, context={"request": request}, )
        paginated_data = self.get_paginated_response(serializer.data)
        return ResponseWrapper(data=paginated_data.data, msg="Success")

    def home_page_details(self, request, *args, **kwargs):
        top_recommended_daily_needs_qs = (
            Product.objects.filter(
                is_public=True, categories__partner_type__name="Daily Needs"
            )
            .exclude(structure="CHILD")
            .distinct()
        )

        top_recommended_market_place_qs = (
            Product.objects.filter(
                is_public=True, categories__partner_type__name="Marketplace"
            )
            .exclude(structure="CHILD")
            .distinct()
        )

        top_recommended_service_qs = (
            Product.objects.filter(
                is_public=True, categories__partner_type__name="Service"
            )
            .exclude(structure="CHILD")
            .distinct()
        )

        context = {
            "top_recommended_daily_needs_list": CustomProductListSerializer(
                instance=top_recommended_daily_needs_qs,
                many=True,
                context={"request": request},
            ).data,
            "top_recommended_market_places_list": CustomProductListSerializer(
                instance=top_recommended_market_place_qs,
                many=True,
                context={"request": request},
            ).data,
            "top_recommended_service_list": CustomProductListSerializer(
                instance=top_recommended_service_qs,
                many=True,
                context={"request": request},
            ).data,
        }

        return ResponseWrapper(data=context, msg="Success", status=200)

    def landing_page_details(self, request,partner_type_name, *args, **kwargs):
        product_type_qs = PartnerType.objects.filter(name__icontains=partner_type_name).last()

        category_qs = Category.objects.filter(partner_type=product_type_qs)

        flash_sell_qs = (
            Product.objects.filter(
                categories__partner_type=product_type_qs, is_public=True
            )
            .exclude(structure="CHILD")
            .distinct()
        )

        top_recommended_product_qs = (
            Product.objects.filter(
                categories__partner_type=product_type_qs, is_public=True
            )
            .exclude(structure="CHILD")
            .distinct()
        )

        trending_product_qs = (
            Product.objects.filter(
                categories__partner_type=product_type_qs, is_public=True
            )
            .exclude(structure="CHILD")
            .distinct()
        )

        best_selling_product_qs = (
            Product.objects.filter(
                categories__partner_type=product_type_qs, is_public=True
            )
            .exclude(structure="CHILD")
            .distinct()
        )

        lowest_price_product_qs = (
            Product.objects.filter(
                categories__partner_type=product_type_qs, is_public=True
            )
            .exclude(structure="CHILD")
            .order_by("stockrecords__price")
            .distinct()
        )
        # strategy = Selector().strategy()
        # a = strategy.fetch_for_product(qs.last()).price
        # float(a.excl_tax)

        featured_product_qs = (
            Product.objects.filter(
                categories__partner_type=product_type_qs, is_public=True
            )
            .exclude(structure="CHILD")
            .distinct()
        )
        context = {
            # "category_list": CustomCategorySerializer(
            #     instance=category_qs, many=True, context={"request": request}
            # ).data,
            "flash_sell_list": CustomProductListSerializer(
                instance=flash_sell_qs, many=True, context={"request": request}
            ).data,
            "top_recommended_product_list": CustomProductListSerializer(
                instance=top_recommended_product_qs,
                many=True,
                context={"request": request},
            ).data,
            "trending_product_list": CustomProductListSerializer(
                instance=trending_product_qs, many=True, context={"request": request}
            ).data,
            "best_selling_product_list": CustomProductListSerializer(
                instance=best_selling_product_qs,
                many=True,
                context={"request": request},
            ).data,
            "lowest_price_product_list": CustomProductListSerializer(
                instance=lowest_price_product_qs.distinct(),
                many=True,
                context={"request": request},
            ).data,
            "featured_product_list": CustomProductListSerializer(
                instance=featured_product_qs, many=True, context={"request": request}
            ).data,
        }
        # print('jjjjjjjjjjjjjjjjjj')

        return ResponseWrapper(data=context, msg="Success", status=200)

    def category_wise_product_list(self, request, slug, *args, **kwargs):
        self.filterset_class=CustomProductFilter
        qs = self.filter_queryset(Product.objects.filter(categories__slug=slug))
        if not qs:
            return ResponseWrapper(error_msg="Products Not Found")
        page_qs = self.paginate_queryset(qs)
        serializer = CustomProductSerializer(
            instance=page_qs, many=True, context={"request": request}
        )
        paginated_data = self.get_paginated_response(serializer.data)
        return ResponseWrapper(data=paginated_data.data, msg="Success")

    def recent_marketplace_product_list(self, request, *args, **kwargs):
        self.filterset_class=CustomProductFilter
        qs = self.filter_queryset(Product.objects.all().order_by('-id'))
        page_qs = self.paginate_queryset(qs)
        serializer = CustomProductSerializer(
            instance=page_qs, many=True, context={"request": request}
        )
        paginated_data = self.get_paginated_response(serializer.data)
        return ResponseWrapper(data=paginated_data.data, msg="Success")

    def most_popular_marketplace_product_list(self, request, *args, **kwargs):
        self.filterset_class=CustomProductFilter
        qs = self.filter_queryset(Product.objects.all().order_by('?'))
        page_qs = self.paginate_queryset(qs)
        serializer = CustomProductSerializer(
            instance=page_qs, many=True, context={"request": request}
        )
        paginated_data = self.get_paginated_response(serializer.data)
        return ResponseWrapper(data=paginated_data.data, msg="Success")

    def popular_marketplace_product_list(self, request, *args, **kwargs):
        self.filterset_class=CustomProductFilter
        qs = self.filter_queryset(Product.objects.all().order_by('?'))
        page_qs = self.paginate_queryset(qs)
        serializer = CustomProductSerializer(
            instance=page_qs, many=True, context={"request": request}
        )
        paginated_data = self.get_paginated_response(serializer.data)
        return ResponseWrapper(data=paginated_data.data, msg="Success")

    def top_recommended_daily_needs_product_list(self, request, *args, **kwargs):
        top_recommended_daily_needs_qs = self.filter_queryset(
            Product.objects.filter(
                is_public=True, categories__partner_type__name="Daily Needs"
            )
            .exclude(structure="CHILD")
            .distinct()
        )

        page_qs = self.paginate_queryset(top_recommended_daily_needs_qs)
        serializer = CustomProductListSerializer(instance=page_qs, many=True, context={"request": request})
        paginated_data = self.get_paginated_response(serializer.data)

        return ResponseWrapper(
            data=paginated_data.data,
            status=200
        )

    def top_recommended_services_list(self, request, *args, **kwargs):
        top_recommended_services_qs = self.filter_queryset(
            Product.objects.filter(
                is_public=True, categories__partner_type__name="Service"
            )
            .exclude(structure="CHILD")
            .distinct()
        )

        page_qs = self.paginate_queryset(top_recommended_services_qs)
        serializer = CustomProductListSerializer(instance=page_qs, many=True, context={"request": request})
        paginated_data = self.get_paginated_response(serializer.data)

        return ResponseWrapper(
            data=paginated_data.data,
            status=200
        )


class CategoryViewSet(CustomViewSet):
    serializer_class = CustomCategorySerializer
    queryset = Category.objects.all()
    # pagination_class = LimitOffsetPagination
    lookup_field = "pk"
    pagination_class = CustomPagination
    filterset_class = CustomCategoryFilter
    # filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)

    # def get_pagination_class(self):
    #     if self.action in ['get_list']:
    #         return CustomPagination
    #     else:
    #         return None
    #
    # pagination_class = property(get_pagination_class)

    def list(self, request, *args, **kwargs):
        try:
            qs = self.filter_queryset(self.get_queryset())
        except:
            return ResponseWrapper(error_msg="Category Not Found", error_code=404, status=404)
        filter_qs = []
        for q in qs:
            if q.is_root() == True:
                filter_qs.append(q)
        serializer_class = self.get_serializer_class()
        page_qs = self.paginate_queryset(filter_qs)
        serializer = CustomCategoryListSerializer(instance=page_qs, many=True)
        paginated_data = self.get_paginated_response(serializer.data)
        return ResponseWrapper(data=paginated_data.data, msg="Success", status=200)

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        qs = self.get_queryset()

        object = qs.filter(pk = pk)
        if not object.exists():
            return ResponseWrapper(error_msg="Category not found", error_code=404, status=404)

        serializer = self.get_serializer(object.first())
        return ResponseWrapper(data = serializer.data, msg="Category Details", status=200)

    def create(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        image = request.data.get("image")
        thumbnail_image = request.data.get("thumbnail_image")
        partner_type  = request.data.get("partner_type")
        parent_category = request.data.get("parent_category")
        description  = request.data.get("description")
        name = request.data.get('name')

        if not image:
            return ResponseWrapper(error_msg='No image found, Please provide a valid image', error_code=400, status=400)
        if not thumbnail_image:
            return ResponseWrapper(error_msg='No Thumbnail image found, Please provide a valid image for Thumbnail', error_code=400, status=400)

        if not  PartnerType.objects.filter(id=partner_type).exists():
            return ResponseWrapper(error_msg='No Valid Partner type is provided', error_code=400, status = 400) 

        if not description:
            return ResponseWrapper(error_msg='No Description found, Please provide a Description', error_code=400, status=400)

        if serializer.is_valid():
            if parent_category is None:
                category_qs = Category.objects.filter(name = name,partner_type_id = request.data.get('partner_type')).last()
                if category_qs:
                    return ResponseWrapper(error_msg='This Category Name Already Exists', status = 400, error_code =400)
                name_list = []
                name_list.append(name)
                # print(name_list)   
                parent = create_from_sequence(name_list)
                qs = serializer.update(
                            instance=parent[0], validated_data=serializer.validated_data
                        )
                        #parent_category_qs.append(child)

                serializer = CustomCategorySerializer(instance=qs)
                #serializer = CustomCategorySerializer(instance=parent)
                return ResponseWrapper(data=serializer.data, msg="created", status=201)
            else:
                # parent = get_object_or_404(Category, pk=parent_category)
                # request.data['depth'] = int(parent.depth)+1

                serializer = CustomChildCategorySerializer(data=request.data)
                
                if serializer.is_valid():
                    name = serializer.validated_data.get("name")
                    parent_category = serializer.validated_data.pop("parent_category")

                    parent_category_qs = Category.objects.filter(id=parent_category).last()
                    if not parent_category_qs:
                        return ResponseWrapper(
                            error_msg="Parent Category is Not Found", error_code=400, status=400
                        )

                    # # get category
                    # parent = get_object_or_404(Category, pk=parent_category)

                    # check child category with this name
                    try:
                        '''
                        Is there any category exist at the same name.
                        cant perform this checking at the begining because same child is 
                        allowed under different parent.
                        '''
                        child = parent_category_qs.get_children().get(name=name)
                        return ResponseWrapper(
                            error_msg="This Category is already exists.",
                            error_code=400,
                            status=400
                        )
                    except Category.DoesNotExist:
                        '''
                        If there are no existing category at the same name, then create new one
                        '''
                      
                        # print(parent_category_qs.numchild)
                        child = parent_category_qs.add_child(name=name)
                        child.save()
                        qs = serializer.update(
                            instance=child, validated_data=serializer.validated_data
                        )
                        # print(parent_category_qs.numchild)
                        parent_category_qs.save()
                        child.save()
                        serializer = CustomCategorySerializer(instance=qs)
                        return ResponseWrapper(data=serializer.data, msg="created", status=200)
                else:
                    return ResponseWrapper(error_msg=serializer.errors, error_code=400, status=400)

        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400, status=400)

    def destroy(self, request, pk, *args, **kwargs):
        qs = Category.objects.filter(id=pk).first()
        if qs:
            qs.delete()
            return ResponseWrapper(status=200, msg="deleted")
        else:
            return ResponseWrapper(error_msg="Category Not Found", error_code=400, status=400)

    def market_place_category_list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(Category.objects.filter(is_public=True, partner_type__name="Marketplace"))

        page_qs = self.paginate_queryset(queryset)
        serializer = CustomCategoryListSerializer(instance=page_qs, many=True)
        paginated_data = self.get_paginated_response(serializer.data)

        return ResponseWrapper(
            data=paginated_data.data,
            status=200
        )

    def daily_needs_category_list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(Category.objects.filter(is_public=True, partner_type__name="Daily Needs"))

        page_qs = self.paginate_queryset(queryset)
        serializer = CustomCategoryListSerializer(instance=page_qs, many=True)
        paginated_data = self.get_paginated_response(serializer.data)

        return ResponseWrapper(
            data=paginated_data.data,
            status=200
        )

    def service_category_list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(Category.objects.filter(is_public=True, partner_type__name="Service"))

        page_qs = self.paginate_queryset(queryset)
        serializer = CustomCategoryListSerializer(instance=page_qs, many=True)
        paginated_data = self.get_paginated_response(serializer.data)

        return ResponseWrapper(
            data=paginated_data.data,
            status=200
        )

    def update(self, request, **kwargs):
            serializer_class = self.get_serializer_class()
            serializer = serializer_class(data=request.data, partial=True)

            partner_type = request.data.get('partner_type')
            if partner_type:
                if not  PartnerType.objects.filter(id=partner_type).exists():
                    return ResponseWrapper(error_msg='No Valid Partner type is provided', error_code=400, status = 400)

            name = request.data.get('name')
            if name:
                category_qs = Category.objects.filter(name = name, partner_type_id = Category.objects.filter(id = kwargs['pk']).last().partner_type).exclude(id = kwargs['pk'] ).last()
                if category_qs:
                    return ResponseWrapper(error_msg='This Category Name Already Exists', status = 400, error_code =400)
            
            # image = request.data.get('image')
            # if image is None:
            #     return ResponseWrapper(error_msg='No image found, Please provide a valid image', error_code=400)
            # if not thumbnail_image:
            # return ResponseWrapper(error_msg='No Thumbnail image found, Please provide a valid image for Thumbnail', error_code=400)
            parent_category = request.data.pop('name')
            if parent_category:
                return ResponseWrapper(error_msg='Parent category can not be changed', status = 400, error_code =400)
            if serializer.is_valid():
                qs = serializer.update(instance=self.get_object(
                ), validated_data=serializer.validated_data)
                serializer = self.serializer_class(instance=qs)
                return ResponseWrapper(data=serializer.data, status=200)
            else:
                return ResponseWrapper(error_msg=serializer.errors, error_code=400, status=400)

# class ChildCategoryViewSet(CustomViewSet):
#     serializer_class = CustomChildCategorySerializer
#     queryset = Category.objects.all()
#     lookup_field = "pk"
#     filterset_class = CustomChildCategoryFilter
#     filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)

#     def list(self, request, *args, **kwargs):
#         try:
#             qs = self.filter_queryset(self.get_queryset())
#         except:
#             return ResponseWrapper(error_msg="Invalid Partner Type", error_code=404, status=404)

#         filter_qs = []
#         for q in qs:
#             if q.is_root() == True:
#                 filter_qs.append(q)

#         # serializer_class = self.get_serializer_class()
#         # serializer = serializer_class(instance=filter_qs, many=True)

#         page_qs = self.paginate_queryset(filter_qs)
#         serializer = CustomChildCategorySerializer(instance=page_qs, many=True)
#         paginated_data = self.get_paginated_response(serializer.data)
#         return ResponseWrapper(data=paginated_data.data, msg="Success", status=200)


#     def create(self, request, *args, **kwargs):
#         serializer_class = self.get_serializer_class()
#         serializer = serializer_class(data=request.data)

#         if serializer.is_valid():
#             name = serializer.validated_data.get("name")
#             parent_category = serializer.validated_data.pop("parent_category")

#             parent_category_qs = Category.objects.filter(id=parent_category).last()
#             if not parent_category_qs:
#                 return ResponseWrapper(
#                     error_msg="Parent Category is Not Found", error_code=400, status=400
#                 )

#             # get category
#             parent = get_object_or_404(Category, pk=parent_category)

#             # check child category with this name
#             try:
#                 '''
#                 Is there any category exist at the same name.
#                 cant perform this checking at the beginning because same child is 
#                 allowed under different parent.
#                 '''
#                 child = parent.get_children().get(name=name)
#                 return ResponseWrapper(
#                     error_msg="This Category is already exists.",
#                     error_code=400,
#                     status=400
#                 )
#             except Category.DoesNotExist:
#                 '''
#                 If there are no existing category at the same name, then create new one
#                 '''
#                 child = parent.add_child(name=name)
#                 # child.path = parent.path + random.randint(3, 9999)
#                 child.save()                
#                 qs = serializer.update(
#                     instance=child, validated_data=serializer.validated_data
#                 )
#                 #parent.append(child)
#                 parent.fix_tree(destructive=False)
#                 serializer = self.serializer_class(instance=qs)
#                 return ResponseWrapper(data=serializer.data, msg="created", status=200)
#         else:
#             return ResponseWrapper(error_msg=serializer.errors, error_code=400, status=400)

#     def retrieve(self, request, *args, **kwargs):
#         pk = kwargs.get("pk")
#         qs = self.get_queryset()

#         object = qs.filter(pk = pk)
#         if not object.exists():
#             return ResponseWrapper(error_msg="Category child not found", error_code=404, status=404)

#         serializer = self.get_serializer(object.first())
#         return ResponseWrapper(serializer.data)


#     def destroy(self, request, pk, *args, **kwargs):
#         qs = Category.objects.filter(id=pk).first()
#         if qs:
#             qs.delete()
#             return ResponseWrapper(status=200, msg="deleted")
#         else:
#             return ResponseWrapper(error_msg="Category Not Found", error_code=400, status=400)

#     def update(self, request, **kwargs):
#         serializer_class = self.get_serializer_class()
#         serializer = serializer_class(data=request.data, partial=True)
        
#         name = request.data.get('name')
#         if name:
#             if Category.objects.filter(name__iexact=name).exclude(**kwargs).exists():
#                 return ResponseWrapper(error_msg="There is another category with same name", error_code=400, status=400)

#         parent_category = request.data.get("parent_category")
#         if parent_category:
#             parent_category_qs = Category.objects.filter(id=parent_category).last()
#             if not parent_category_qs:
#                 return ResponseWrapper(
#                     error_msg="Parent Category is Not Found", error_code=400, status=400
#                 )

#         if serializer.is_valid():
#             qs = serializer.update(instance=self.get_object(
#             ), validated_data=serializer.validated_data)
#             serializer = self.serializer_class(instance=qs)
#             return ResponseWrapper(data=serializer.data, status=200)
#         else:
#             return ResponseWrapper(error_msg=serializer.errors, error_code=400, status=400)


class ZoneWiseProductViewSet(CustomViewSet):
    serializer_class = ZoneWizeProductSerializer
    queryset = Product.objects.all()
    lookup_field = "pk"

    def zone_wise_product(self, request, pk=None):
        queryset = Product.objects.filter(zone_id=pk)
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(instance=queryset, many=True)

    def retrieve(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk")
        qs = Product.objects.filter(zone__id=pk)
        serializer = self.get_serializer(instance=qs, many=True)
        return ResponseWrapper(data= serializer.data, status=200)


class CountryViewSet(CustomViewSet):
    serializer_class = CustomCountrySerializer
    queryset = Country.objects.all()
    lookup_field = "pk"
    pagination_class = CustomPagination
    filterset_class = CustomCountryFilter
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)

    def create(self, request, *args, **kwargs):
        iso_3166_1_a2 = request.data.get('iso_3166_1_a2')
        qs = Country.objects.filter(iso_3166_1_a2 =iso_3166_1_a2).last()
        if qs:
            return ResponseWrapper(
                error_msg='Country is Already Exist, Use Different iso_3166_1_a2 ', 
                error_code=400,
                status=400
            )

        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        if serializer.is_valid():
            qs = serializer.save()
            return ResponseWrapper(
                data=serializer.data, 
                msg='created',
                status=201
            )
        else:
            return ResponseWrapper(
                error_msg=serializer.errors, 
                error_code=400,
                status=400
            )


    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset().order_by('display_order'))
        page_qs = self.paginate_queryset(qs)
        serializer = CustomCountrySerializer(instance=page_qs, many=True)
        paginated_data = self.get_paginated_response(serializer.data)

        return ResponseWrapper(data =paginated_data.data, msg='Success')

    def update(self, request, pk, **kwargs):
        qs = Country.objects.filter(iso_3166_1_a2 = pk).last()
        if not qs:
            return ResponseWrapper(
                error_msg='Country Not Found', 
                error_code=404,
                status=404    
            )

        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, partial=True)

        qs = self.queryset.filter(**kwargs)
        if not qs.exists():
            return ResponseWrapper(
                error_msg="Country Not Found", 
                error_code=404,
                status=404    
            )

        if serializer.is_valid():
            iso_3166_1_a2 = serializer.validated_data.get("iso_3166_1_a2", None)

            if iso_3166_1_a2:
                return ResponseWrapper(
                    error_msg="Can not update read_only iso_3166_1_a2 field",
                    error_code=400,
                    status=400
                )
            qs = serializer.update(
                instance=self.get_object(), validated_data=serializer.validated_data
            )
            serializer = self.serializer_class(instance=qs)
            return ResponseWrapper(
                data=serializer.data,
                msg="updated",
                status=200
            )
        else:
            return ResponseWrapper(
                error_msg=serializer.errors, 
                error_code=400,
                status=400    
            )

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        qs = self.get_queryset()

        country = qs.filter(iso_3166_1_a2__exact = pk)
        if not country.exists():
            return ResponseWrapper(
                error_msg="Country not found", 
                error_code=404,
                status=404
            )

        serializer = self.get_serializer(country.first())
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
                error_msg="Country not found",
                error_code=404,
                status=404
            )


class CategoryChildrenViewSet(CustomViewSet):
    serializer_class = CustomCategorySerializer
    queryset = Category.objects.all()
    filterset_class = CustomCategoryFilter
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)

    def retrieve(self, request, *args, **kwargs):
        pk = self.kwargs.get("pk", None)
        instance = get_object_or_404(Category, pk=pk)
        child = instance.get_children()
        page_qs = self.paginate_queryset(child)
        serializer = self.get_serializer(page_qs, many=True)
        paginated_data = self.get_paginated_response(serializer.data)
        return ResponseWrapper(
            data=paginated_data.data, msg=f"{instance} category children list", status=200
        )
    def child_category_list(self, request,category_id, *args, **kwargs):
        qs = Category.objects.filter(id =category_id).last()
        if not qs:
            return ResponseWrapper(error_msg="Category not found", error_code=404, status=404)
        child = qs.get_children()
        if  not child:
            return ResponseWrapper(error_msg=f"{qs} category doesn't have any child.", status=200
            )
        child = self.filter_queryset(child)
        page_qs = self.paginate_queryset(child)
        serializer = self.get_serializer(page_qs, many=True)
        paginated_data = self.get_paginated_response(serializer.data)
        return ResponseWrapper(
            data=paginated_data.data, msg=f"{qs} category children list", status=200
        )
