from django.urls import path
from customapp.views import *

urlpatterns = [
    path("version/", VersionViewSet.as_view({'get': 'list', 'post': 'create'}), name='version'),
    path("version/<int:pk>/",VersionViewSet.as_view({'get': 'retrieve', 'patch': 'update',  'delete': 'destroy'}), name='version'),
    path("latest_version/",VersionViewSet.as_view({
       'get': 'latest_version'}), name='latest_version'),


    path("product_image/", CustomProductImageViewSet.as_view({'get': 'list'}), name="product_image"),
    path("product_image_create/<int:product_id>/", CustomProductImageViewSet.as_view({'post': 'create'}), name="product_image_create"),
    path("product_image/<int:pk>/", CustomProductImageViewSet.as_view({'get': 'retrieve', 'patch': 'update',  'delete': 'destroy'}), name="product_image"),

    path("stock_record_list/<int:pk>/<int:partner>/", StockRecordListView.as_view(), name='stock_record_list'),
    path("stock_record_specific/<int:pk>/<int:partner>/", StockRecordSpecificView.as_view(), name='stock_record_specific'),

    path("product_review/<int:product_id>/", ProductReviewListView.as_view({"get": "list", 'post':'create'}), name='product_review_list'),
    path("review/<int:pk>/", ProductReviewSpecificView.as_view({"patch": "update",
                                                                    'delete':'destroy',
                                                                    'get':'retrieve'}),
         name='product_reviews'),
    path("product_review_user/", UserProductReviewListView.as_view({"get": "list"}), name='user_product_review_list'),

    path("shipping_address/<pk>/", ShippingAddressSpecificListView.as_view({'get': 'list'}), name='shipping_address_specific'),
    path("billing_address/<pk>/", BillingAddressSpecificListView.as_view({'get': 'list'}), name='billing_address_specific'),

    path('user_address/', UserAddressView.as_view(
        {"get": "customer_address_list", 'post': 'create'}),
         name="user_address"),

    path('all_user_address_list/', UserAddressView.as_view(
        {"get": "list"}),
         name="user_address"),

    path('user_address/<pk>/', UserAddressView.as_view(
        {"patch": "update", 'delete': 'destroy', 'get': 'retrieve'}),
         name="user_address"),
]