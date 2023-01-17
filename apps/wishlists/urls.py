from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import WishlistViewSet, WishlistUserViewSet

router = DefaultRouter()
# router.register("specific", WishlistUserViewSet, basename="wishlist-user")
# router.register("", WishlistViewSet, basename="wishlist")
#


urlpatterns = [
    path("customer_wishlist_create/", WishlistViewSet.as_view(
         {'post': 'create'}),
          name="customer_wishlist_create"),
    path("customer_wishlist_remove/", WishlistViewSet.as_view(
            {'patch': 'customer_wishlist_remove'}),
            name="customer_wishlist_update"),
    path("customer_wishlist/", WishlistViewSet.as_view(
         {'get': 'customer_wishlist'}),
          name="customer_wishlist"),
              ]\
              + router.urls