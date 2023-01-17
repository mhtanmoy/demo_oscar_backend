from django.urls import path

from .views import OrderHistoryViewSet

urlpatterns = [
    path('customer/orders/', OrderHistoryViewSet.as_view({'get': 'list'}, name='order-history')),
    path('customer/orders/<int:pk>/', OrderHistoryViewSet.as_view({'get':'retrieve'}, name='order-history-detail')),
]