from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import *


router = DefaultRouter()
# router.register("product", ProductViewSet, basename="product")
router.register("product/search", ProductSearchViewSet, basename="product-search")
# router.register("product/type", ProductTypeViewSet, basename="product-type")
# router.register("product/attribute", ProductAttributeViewSet, basename="product-attribute")
# router.register("product/attribute/value", ProductAttributeValueViewSet, basename="product-attribute-value")
# router.register("product/stockrecord", ProductStockRecordViewSet, basename="product-stockrecord")


urlpatterns = [
    path('product/type/service/', ServiceTypeProductViewSet.as_view({"get": "list"}), name="service_type_product"),
    path('product/type/marketPlace/', MarketPlaceTypeProductViewSet.as_view({"get": "list"}), name="marketPlace_type_product"),
    path('product/type/dailyNeed/', DailyNeedTypeProductViewSet.as_view({"get": "list"}), name="dailyNeed_type_product"),
    path('product/approve/', ApproveProductView.as_view({"post": "create"}), name="approve_product"),
    path('product_attribute_value_create/<int:product_id>/', ProductAttributeValueViewSet.as_view({"post": "create"}), name="product_attribute_value_create"),
    path('product/attribute/value/', ProductAttributeValueViewSet.as_view({"get": "list"}), name="product_attribute_value"),
    path('product/attribute/value/<int:pk>/', ProductAttributeValueViewSet.as_view({"patch": "update", 'delete': 'destroy', 'get': 'retrieve'}), name="product_attribute_value"),
    path('product_attribute_create/<int:product_class_id>/', ProductAttributeViewSet.as_view({ "post": "create"}), name="product_attribute"),
    path('product/attribute/', ProductAttributeViewSet.as_view({ "get": "list"}), name="product_attribute"),
    path('product/attribute/<int:pk>/', ProductAttributeViewSet.as_view({"patch": "update", 'delete': 'destroy', 'get': 'retrieve'}), name="product_attribute"),
    path('product/stockrecord/', ProductStockRecordViewSet.as_view({"get": "list", "post": "create"}), name="product_stockrecord"),
    path('product/stockrecord/<int:pk>/', ProductStockRecordViewSet.as_view({"patch": "update", 'delete': 'destroy', 'get': 'retrieve'}), name="product_stockrecord"),
    path('product/type/', ProductTypeViewSet.as_view({"get": "list", "post": "create"}), name="product_type"),
    path('product/type/<int:pk>/', ProductTypeViewSet.as_view({"patch": "update", 'delete': 'destroy', 'get': 'retrieve'}), name="product_type"),
    path('product/', ProductViewSet.as_view(
        {"get": "list", 'post': 'create'}),
         name="product"),
    path('product/<pk>/', ProductViewSet.as_view(
        {"patch": "update", 'delete': 'destroy', 'get': 'retrieve'}),
         name="product"),
    # path('product_details/<slug>/', ProductViewSet.as_view(
    #     {'get': 'product_details'}),
    #      name="product_details"),
    path('discount/', DiscountViewSet.as_view(
        {"get": "list", 'post': 'create'}),
         name="discount"),
    path('discount/<pk>/', DiscountViewSet.as_view(
        {"patch": "update", 'delete': 'destroy', 'get': 'retrieve'}),
         name="discount"),

    path('promocode/', PromoCodeViewSet.as_view(
        {"get": "list", 'post': 'create'}),
         name="promocode"),
    path('promocode/<pk>/', PromoCodeViewSet.as_view(
        {"patch": "update", 'delete': 'destroy', 'get': 'retrieve'}),
         name="promocode"),

    path('discount_product/', DiscountViewSet.as_view({"post": "apply_discount_on_product"}), name="apply_discount_on_product"),
    path('discount_category/', DiscountViewSet.as_view({"post": "apply_discount_on_category_of_product"}), name="apply_discount_on_category_of_product"),

    path('valid_discounts/', DiscountViewSet.as_view({'get': 'valid_discount_list'}, name='valid_discounts')),
    path('valid_promo_codes/', PromoCodeViewSet.as_view({'get': 'valid_promo_code_list'}, name='valid_promo_codes')),
]

urlpatterns += router.urls