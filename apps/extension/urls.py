from django.urls import path

from .views import *

urlpatterns = [
    # path(
    #     "child_category_list/<category_id>/",
    #     CategoryViewSet.as_view({"get": "child_category_list"}),
    #     name="child_category_list",
    # ),
    # path(
    #     "category/child/",
    #     ChildCategoryViewSet.as_view({"get": "list"}),
    #     name="child-category",
    # ),
    # path(
    #     "category/child/<pk>/",
    #     ChildCategoryViewSet.as_view(
    #         {"patch": "update", "get": "retrieve", "delete": "destroy"}
    #     ),
    #     name="child-category",
    # ),
    path(
        "category/",
        CategoryViewSet.as_view({"get": "list", "post": "create"}, name="category"),
    ),
    path(
        "category/<pk>/",
        CategoryViewSet.as_view(
            {"get": "retrieve", "patch": "update", "delete": "destroy"},
            name="category",
        ),
    ),
    path(
        "zone_wise_product/<int:pk>/",
        ZoneWiseProductViewSet.as_view({"get": "retrieve"}),
        name="zone_wise_product",
    ),
    path(
        "category_wise_product_list/<slug>/",
        HomePageViewSet.as_view({"get": "category_wise_product_list"}),
        name="category_wise_product_list",
    ),
    path("recent_marketplace_product_list/",
        HomePageViewSet.as_view({"get": "recent_marketplace_product_list"}),
        name="recent_marketplace_product_list",
    ),
    path("most_popular_marketplace_product_list/",
        HomePageViewSet.as_view({"get": "most_popular_marketplace_product_list"}),
        name="most_popular_marketplace_product_list",
    ),
    path("popular_marketplace_product_list/",
        HomePageViewSet.as_view({"get": "popular_marketplace_product_list"}),
        name="popular_marketplace_product_list",
    ),
    path(
        "country/",
        CountryViewSet.as_view({"get": "list", "post": "create"}),
        name="country",
    ),
    path(
        "country/<str:pk>/",
        CountryViewSet.as_view(
            {"patch": "update", "get": "retrieve", "delete": "destroy"}
        ),
        name="country",
    ),
    path(
        "home_page_details/",
        HomePageViewSet.as_view({"get": "home_page_details"}),
        name="home_page_details",
    ),
    path(
        "landing_page_details/<partner_type_name>/",
        HomePageViewSet.as_view({"get": "landing_page_details"}),
        name="landing_page_details",
    ),
    path(
        "top_recommended_market_place_product_list/",
        HomePageViewSet.as_view({"get": "top_recommended_market_place_product_list"}),
        name="top_recommended_market_place_product_list",
    ),
    path(
        "market_place_trending_product_list/",
        HomePageViewSet.as_view({"get": "market_place_trending_product_list"}),
        name="market_place_trending_product_list",
    ),
    path(
        "market_place_best_selling_product_list/",
        HomePageViewSet.as_view({"get": "market_place_best_selling_product_list"}),
        name="market_place_best_selling_product_list",
    ),
    path(
        "market_place_lowest_price_product_list/",
        HomePageViewSet.as_view({"get": "market_place_lowest_price_product_list"}),
        name="market_place_lowest_price_product_list",
    ),
    path(
        "market_place_featured_product_list/",
        HomePageViewSet.as_view({"get": "market_place_featured_product_list"}),
        name="market_place_featured_product_list",
    ),
    path(
        "market_place_best_seller_list/",
        HomePageViewSet.as_view({"get": "market_place_best_seller_list"}),
        name="market_place_best_seller_list",
    ),
    path(
        "top_recommended_daily_needs_product_list/",
        HomePageViewSet.as_view({"get": "top_recommended_daily_needs_product_list"}),
        name="top_recommended_daily_needs_product_list",
    ),
    path(
        "top_recommended_services_list/",
        HomePageViewSet.as_view({"get": "top_recommended_services_list"}),
        name="top_recommended_services_list",
    ),
    path(
        "market_place_category_list/",
        CategoryViewSet.as_view({"get": "market_place_category_list"}),
        name="market_place_category_list",
    ),
    path(
        "daily_needs_category_list/",
        CategoryViewSet.as_view({"get": "daily_needs_category_list"}),
        name="daily_needs_category_list",
    ),
    path(
        "service_category_list/",
        CategoryViewSet.as_view({"get": "service_category_list"}),
        name="service_category_list",
    ),
    # path('market_place/',
    #       HomePageViewSet.as_view({"get": "market_place_details"}),
    #       name="market_place_details"),
]
