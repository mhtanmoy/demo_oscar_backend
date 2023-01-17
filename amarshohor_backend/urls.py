from django.apps import apps
from django.urls import include, path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from django.conf import settings
from django.views.static import serve

# from django.conf.urls import url
from rest_framework import permissions
from drf_yasg2.views import get_schema_view
from drf_yasg2 import openapi
from apps.oscar_invoices import urls as oscar_invoices_urls


schema_view = get_schema_view(
    openapi.Info(
        title="Amar Shohor Api",
        default_version="v1",
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@arabika.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

swagger_url = [
    path(
        "api/swagger.json/", schema_view.without_ui(cache_timeout=0), name="schema-json"
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    # The Django admin is not officially supported; expect breakage.
    # Nonetheless, it's often useful for debugging.
    path("admin/", admin.site.urls),
    path("api/", include("apps.extension.urls")),
    path("", include("shop.urls")),
    path("api/", include("oscarapi.urls")),
    path("auth/", include("authentications.urls")),
    path("api/", include("customapp.urls")),
    path("allauth/", include("allauth.urls")),
    path("invoices/", include("apps.oscar_invoices.urls")),
    path("", include(apps.get_app_config("oscar").urls[0])),
    # Django Oscar Promotions
    # path("", apps.get_app_config("oscar_promotions").urls),
    # path("dashboard/promotions/", apps.get_app_config("oscar_promotions_dashboard").urls),
    # oscar accounts
    path("api/dashboard/accounts/", apps.get_app_config("accounts_dashboard").urls),
    path("api/", include("accounts.urls")),
    path("api/", include("apps.wishlists.urls")),
    path("api/order/", include("apps.order.urls")),
    # product
    path("api/", include("apps.catalogue.urls")),
    # zone
    path("api/", include("apps.partner.urls")),
    # order history
    path("api/", include("apps.customer.urls")),
    # third-party
    path("api/third_party/", include("apps.third_party.urls")),
] + swagger_url

if settings.DEBUG:
    urlpatterns = urlpatterns + static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
    urlpatterns = urlpatterns + static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
