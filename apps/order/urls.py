from django.urls import path

from .views import *

urlpatterns = [
    path(
        "order_details/<order_no>/",
        OrderViewSet.as_view({"get": "order_details"}, name="order_details"),
    ),
    path(
        "customer_order_history/",
        OrderViewSet.as_view(
            {"get": "customer_order_history"}, name="customer_order_history"
        ),
    ),
    path(
        "customer_cancel_order_history/",
        OrderViewSet.as_view(
            {"get": "customer_cancel_order_history"}, name="customer_cancel_order_history"
        ),
    ),
    path(
        "schedule/",
        ScheduleViewSet.as_view({"get": "list", "post": "create"}),
        name="schedule",
    ),
    path(
        "schedule/<int:pk>/",
        ScheduleViewSet.as_view(
            {
                "get": "retrieve",
                "patch": "update",
                "delete": "destroy",
            }
        ),
        name="schedule",
    ),
    path(
        "order_line_confirm/",
        OrderLineViewSet.as_view({"patch": "confirm"}),
        name="order_line",
    ),
    path(
        "order_line_unavailable/",
        OrderLineUnavailableViewSet.as_view({"patch": "unavailable"}),
        name="order_line",
    ),
    path(
        "order_line_delivered/",
        OrderLineDeliveredViewSet.as_view({"patch": "delivered"}),
        name="order-line-delivered",
    ),
    path(
        "order_cancel/",
        OrderCancelViewSet.as_view({"patch": "create"}),
        name="order_cancel",
    ),
    path(
        "order_cancel_by_user/",
        OrderCancelByUserViewSet.as_view({"patch": "order_cancel"}),
        name="order-cancel-user",
    ),
    path(
        "order_item_cancel/",
        OrderItemCancelViewSet.as_view({"patch": "create"}),
        name="order-item-cancel",
    ),
    path(
        "create/", OrderCreateViewSet.as_view({"post": "create"}), name="order-create"
    ),
    path(
        "cart/add/", OrderCreateViewSet.as_view({"post": "single_order_create"}), name="single_order_create"
    ),
    path(
        "reorder/",
        OrderReorderViewSet.as_view({"post": "order_reorder_create"}),
        name="order-reorder",
    ),
    path(
        "order_count_per_schedule/",
        OrderCountPerScheduleViewSet.as_view({"get": "list", "post": "create"}),
        name="order_count_per_schedule",
    ),
    path(
        "order_count_per_schedule/<pk>/",
        OrderCountPerScheduleViewSet.as_view(
            {"patch": "update", "delete": "destroy", "get": "retrieve"}
        ),
        name="order_count_per_schedule",
    ),
    path(
        "orders_merchant/<order_no>/",
        OrderViewSet.as_view({"get": "order_details"}),
        name="orders_merchant",
    ),
    path(
        "orders_list/",
        OrderViewSet.as_view({"get": "list"}),
        name="orders_list",
    ),
    path(
        "picked/",
        StatusWiseOrderViewSet.as_view({"get": "picked"}),
        name="order-picked",
    ),
    path(
        "on_the_way/",
        StatusWiseOrderViewSet.as_view({"get": "on_the_way"}),
        name="order-on-the-way",
    ),
    path(
        "delivered/",
        StatusWiseOrderViewSet.as_view({"get": "delivered"}),
        name="order-delivered",
    ),
    path(
        "status/placed/",
        OrderPlacedSerializer.as_view({"post": "status_change"}),
        name="order-status-placed",
    ),
    path(
        "order_update/<int:id>/",
        OrderLineViewSet.as_view({"patch": "order_line_update"}, name="order_update"),
    ),
]
