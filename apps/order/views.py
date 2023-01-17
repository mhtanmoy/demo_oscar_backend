from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny

from rest_framework.permissions import IsAuthenticated
from apps.catalogue.models import Category, Product, PromoCode
from utils.custom_viewset import CustomViewSet
from utils.response_wrapper import ResponseWrapper
from utils.custom_pagination import CustomPagination
from apps.order.models import *
from oscarapi.serializers.checkout import Country
from oscar.apps.order.abstract_models import AbstractLine
from oscar.apps.partner.models import StockRecord

from oscar.apps.basket.models import Basket as Cart
from django.utils.timezone import datetime

from .models import *
from .serializers import *
from .filters import *
from accounts.models import UserAccount as User
from oscar.apps.order.models import Line
from oscarapi.basket import operations
from oscar.apps.basket import signals
from django.contrib.sites.models import Site
from django_filters.rest_framework import DjangoFilterBackend
from oscar.apps.order.models import BillingAddress, ShippingAddress
from oscar.apps.order.utils import OrderNumberGenerator

# from apps.partner.serializers import OrderCountPerScheduleSerializer
# from rest_framework.permissions import IsAdminUser
from drf_yasg2.utils import swagger_auto_schema
from rest_framework import filters, permissions, status, viewsets
from apps.partner.models import Partner
from apps.catalogue.models import Discount

from apps.partner.models import Partner, PartnerType, Zone
from accounts.models import Employee, EmployeeCategory
from .tasks import (
    send_mail_service,
    send_order_confirm_notification,
    send_order_pending_notification,
    send_order_delivered_notification,
    send_order_cancel_notification,
    send_order_item_cancel_notification,
    send_order_unavailable_notification,
)

from oscar_invoices.models import Invoice
from oscar_invoices.utils import InvoiceCreator
from oscar_invoices.models import LegalEntity, LegalEntityAddress


# Create your views here.

from utils.permissions import CheckCustomPermission, IsOwnerOrReadOnly

class OrderViewSet(CustomViewSet):
    serializer_class = OrderDetailsSerializer
    queryset = Order.objects.all()
    lookup_field = "pk"
    filterset_class = OrderDetailsFilter
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_fields = ("status","zone")

    def get_serializer_class(self):
        # if self.action == 'create':
        #     self.serializer_class = CreateOrderSerializer
        # else:
        #     self.serializer_class = CreateOrderSerializer

        return self.serializer_class

    def get_permissions(self):
        permission_classes = []
        if self.action in ["customer_order_history"]:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    def orders_list(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        employee_qs = Employee.objects.filter(user=user).first()

        if employee_qs and employee_qs.employee_category.name == "Merchant" and employee_qs.is_active:
            partner = Partner.objects.filter(users=employee_qs.user).first()
            order_qs = Line.objects.filter(partner=partner).values("order").distinct()
            order_list = []
            for order in order_qs:
                order_list.append(order["order"])
            order_list_qs = Order.objects.filter(id__in=order_list).order_by("-date_placed")
            page_qs = self.paginate_queryset(order_list_qs)
            if page_qs is not None:
                serializer = OrderDetailsSerializer(instance=page_qs, many=True)
                paginated_data = self.get_paginated_response(serializer.data)
                return ResponseWrapper(
                    msg="Merchant Order List",
                    data=paginated_data.data,
                )
            else:
                return ResponseWrapper(
                    msg="Customer Order List",
                    data=[],
                )
        elif employee_qs and employee_qs.employee_category.name == "Portfolio_Manager" and employee_qs.is_active:
            # all orders for now until we get the zone
            qs = self.filter_queryset(Order.objects.all())
            page_qs = self.paginate_queryset(qs)
            if page_qs is not None:
                serializer = OrderDetailsSerializer(instance=page_qs, many=True)
                paginated_data = self.get_paginated_response(serializer.data)
                return ResponseWrapper(
                    msg="Portfolio_Manager Order List",
                    data=paginated_data.data,
                )
            else:
                return ResponseWrapper(
                    msg="Customer Order List",
                    data=[],
                )
            
        elif employee_qs and employee_qs.employee_category.name == "Operation_Manager" and employee_qs.is_active:
            # all orders for now until we get the zone
            qs = self.filter_queryset(Order.objects.all())
            page_qs = self.paginate_queryset(qs)
            if page_qs is not None:
                serializer = OrderDetailsSerializer(instance=page_qs, many=True)
                paginated_data = self.get_paginated_response(serializer.data)
                return ResponseWrapper(
                    msg="Operation_Manager Order List",
                    data=paginated_data.data,
                )
            else:
                return ResponseWrapper(
                    msg="Customer Order List",
                    data=[],
                )
        
        else:

            qs = self.filter_queryset(Order.objects.filter(user=user))
            page_qs = self.paginate_queryset(qs)
            if page_qs is not None:
                serializer = OrderDetailsSerializer(instance=page_qs, many=True)
                paginated_data = self.get_paginated_response(serializer.data)
                return ResponseWrapper(
                    msg="Customer Order List",
                    data=paginated_data.data,
                )
            else:
                return ResponseWrapper(
                    msg="Customer Order List",
                    data=[],
                )


    def order_details(self, request, order_no, *args, **kwargs):
        qs = Order.objects.filter(number=order_no).last()

        if not qs:
            return ResponseWrapper(error_msg="Order details not found",error_code=404, status=404)

        serializer = self.serializer_class(instance=qs)

        return ResponseWrapper(data=serializer.data, status=200)
    def customer_order_history(self, request, *args, **kwargs):
        user_qs = request.user
        # qs = Order.objects.filter(user=user_qs)
        qs = self.filter_queryset(Order.objects.filter(user=user_qs))
        if not qs:
            return ResponseWrapper(error_msg="False", status=404)
        serializer = self.serializer_class(instance=qs, many=True)

        order_dict = {"marketPlace": [], "service": [], "dailyNeeds": []}
        for order in serializer.data:
            if order["number"][-1] == "M":
                order_dict["marketPlace"].append(order)
            elif order["number"][-1] == "S":
                order_dict["service"].append(order)
            elif order["number"][-1] == "D":
                order_dict["dailyNeeds"].append(order)
        return ResponseWrapper(order_dict, status=200)
    def customer_cancel_order_history(self, request, *args, **kwargs):
        user_qs = request.user
        qs = Order.objects.filter(user=user_qs, status='Cancelled')
        if not qs:
            return ResponseWrapper(error_msg="False", status=404)
        serializer = self.serializer_class(instance=qs, many=True)

        order_dict = {"marketPlace": [], "service": [], "dailyNeeds": []}
        for order in serializer.data:
            if order["number"][-1] == "M":
                order_dict["marketPlace"].append(order)
            elif order["number"][-1] == "S":
                order_dict["service"].append(order)
            elif order["number"][-1] == "D":
                order_dict["dailyNeeds"].append(order)
        return ResponseWrapper(order_dict, status=200)


class ScheduleViewSet(CustomViewSet):
    serializer_class = ScheduleSerializer
    pagination_class = CustomPagination
    queryset = Schedule.objects.all()
    lookup_field = "pk"
    filterset_class = ScheduleFilter
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_fields = ("is_active",)

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        serializer_class = self.get_serializer_class()
        page_qs = self.paginate_queryset(qs)
        serializer = serializer_class(instance=page_qs, many=True)
        paginated_data = self.get_paginated_response(serializer.data)
        return ResponseWrapper(data=paginated_data.data, msg="Success")

    # def get_permissions(self):
    #     """ Authenticated User can see schedule and Only Admin can create, update or delete Schedule """
    #     if self.action == "list" or self.action == "retrieve":
    #         permission_classes = [(CheckCustomPermission("accounts.custom_view_all_order") | IsAdminUser)] # using parentheses
    #         #permission_classes = [AllowAny]
    #     elif self.action == "create":
    #         permission_classes = [(CheckCustomPermission("accounts.custom_add_order") | IsAdminUser)]
    #         #permission_classes = [IsAuthenticated]
    #     elif self.action == "destroy" or self.action == "update" :
    #         permission_classes = [(CheckCustomPermission("accounts.custom_delete_order") | IsAdminUser)]
    #         #permission_classes = [IsAuthenticated]
    #     else:
    #         permission_classes = [IsAdminUser]
    #     return [permission() for permission in permission_classes]

    def destroy(self, request, **kwargs):
        qs = self.queryset.filter(**kwargs)
        if not qs.exists():
            return ResponseWrapper(error_msg="Schedule Not found", error_code=404, status=404)
        if qs:
            qs.first().delete()
            return ResponseWrapper(status=200, msg="deleted")
        else:
            return ResponseWrapper(error_msg="failed to delete", error_code=400, status=400)

    def update(self, request, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, partial=True)

        qs = self.queryset.filter(**kwargs)
        if not qs.exists():
            return ResponseWrapper(error_msg="Schedule Not Found", error_code=404, status=404)

        if serializer.is_valid():
            start_time = request.data.get('start_time')
            end_time = request.data.get('end_time')

            if start_time > end_time:
                return ResponseWrapper(error_msg="StartTime must be smaller than EndTime", error_code=400, status=400)
            if start_time == end_time:
                return ResponseWrapper(error_msg="StartTime and EndTime can not be equal", error_code=400, status=400)

            qs = Schedule.objects.filter(start_time=start_time, end_time=end_time).exclude(id=kwargs["pk"])

            if qs.exists():
                return ResponseWrapper(error_msg="Schedule is already exists", error_code=400, status=400)

            qs = serializer.update(instance=self.get_object(
            ), validated_data=serializer.validated_data)
            serializer = self.serializer_class(instance=qs)
            return ResponseWrapper(data=serializer.data)
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400, status=400)


    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     start_time = request.data.get('start_time')
    #     end_time = request.data.get('end_time')
    #     qs = Schedule.objects.filter(start_time=start_time, end_time=end_time)
    #     if qs.exists:
    #         return ResponseWrapper(error_msg='Schedule is Already Created', status=400)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    #     return ResponseWrapper(serializer.data, status=200, headers=headers)

    def create(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        if serializer.is_valid():
            start_time = serializer.validated_data.get("start_time")
            end_time = serializer.validated_data.get("end_time")

            qs = self.get_queryset().filter(start_time=start_time, end_time=end_time)
            if qs.exists():
                return ResponseWrapper(error_msg="Schedule already exists", error_code=400, status=400)

            if start_time > end_time:
                return ResponseWrapper(error_msg="StartTime must be smaller than EndTime", error_code=400, status=400)
            if start_time == end_time:
                return ResponseWrapper(error_msg="StartTime and EndTime can not be equal", error_code=400, status=400)

            qs = serializer.save()
            return ResponseWrapper(data=serializer.data, msg='Schedule created', status=201)
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400, status=400)

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        qs = self.get_queryset()

        schedule = qs.filter(pk = pk)
        if not schedule.exists():
            return ResponseWrapper(error_msg="Schedule not found", error_code=404, status=404)

        serializer = self.get_serializer(schedule.first())
        return ResponseWrapper(serializer.data)


# class OrderLineViewSet(viewsets.ModelViewSet):

#     def confirm(self, request, *args, **kwargs):
#         try:
#             abstractLine_ids = request.data.get('id')

#             abstractLine_qs = Line.objects.get(id=abstractLine_id)

#             product_qs = Product.objects.get(id=abstractLine_qs.product.id)

#             partner_qs = Partner.objects.get(id=abstractLine_qs.partner.id)

#             if abstractLine_qs.status == 'Confirmed':

#                 return ResponseWrapper(error_msg='Order Already Confirmed', status=400)
#             elif abstractLine_qs.status == 'Cancelled':

#                 return ResponseWrapper(error_msg='Order Already Cancelled', status=400)
#             elif abstractLine_qs.status == 'Pending':

#                 if partner_qs.partner_type.name == 'Marketplace' or partner_qs.partner_type.name == 'Service':

#                     if product_qs.is_public:

#                         abstractLine_qs.status = 'Confirm'
#                         abstractLine_qs.save()
#                         return ResponseWrapper(
#                             {'msg': 'Order Confirmed Successfully'}
#                         )
#                     else:
#                         return ResponseWrapper(error_msg='Product Not Public', status=400)
#                 else:
#                     return ResponseWrapper(error_msg='Partner is not matching', status=400)
#             else:
#                 return ResponseWrapper(error_msg='Order Cannot be confirmed', status=400)
#         except Exception as e:
#             return ResponseWrapper(
#                 error_msg = str(e),
#                 status = 400
#             )

class OrderLineViewSet(CustomViewSet):
    serializer_class = OrderDetailsSerializer
    queryset = Order.objects.all()
    lookup_field = "pk"
    logging_methods = ["GET", "POST", "PATCH", "DELETE"]

    def get_serializer_class(self):
        if self.action in ["confirm"]:
            self.serializer_class = OrderItemSerializer
        else:
            self.serializer_class = OrderNumberSerializer
        return self.serializer_class

    def confirm(self, request, *args, **kwargs):
        # order_line_list_qs = self.get_serializer(data=request.data, many=True)
        order_line_list_qs = request.data.get("order_item_id")
        try:
            # Line_ids = request.data.get('ids')
            list_of_error = []
            # order_id = -9999
            qs = Line.objects.filter(id=order_line_list_qs[0]).last()

            order_qs = Order.objects.filter(number=qs.order.number).last()

            for order_line_id in order_line_list_qs:
                line_qs = Line.objects.filter(id=order_line_id).last()
                product_qs = Product.objects.filter(id=line_qs.product.id).last()
                partner_qs = Partner.objects.filter(id=line_qs.partner.id).last()

                if line_qs.status == "Confirm":
                    list_of_error.append(
                        "Order Already Confirmed for Order Line ID: " + str(line_qs.id)
                    )
                elif line_qs.status == "Cancelled":
                    list_of_error.append(
                        "Order Already Cancelled for Order Line ID: " + str(line_qs.id)
                    )
                elif line_qs.status == "Pending":
                    try:
                        if (
                            partner_qs.partner_type.name == "Marketplace"
                            or partner_qs.partner_type.name == "Service"
                        ):
                            if product_qs.is_public:
                                if line_qs.order.number == order_qs.number:
                                    line_qs.status = "Confirm"
                                    line_qs.save()
                                    send_order_confirm_notification.delay(
                                        line_qs.order.number
                                    )
                                    order_id = line_qs.order.id
                                else:
                                    list_of_error.append(
                                        "Order ID not matching for Order Line ID: "
                                        + str(line_qs.id)
                                    )
                            else:
                                list_of_error.append(
                                    "Product Not Public for Order Line ID: "
                                    + str(line_qs.id)
                                )
                        else:
                            list_of_error.append(
                                "Partner is not matching for Order Line ID: "
                                + str(line_qs.id)
                            )
                    except Exception as e:
                        list_of_error.append(
                            str(e) + " for Order Line ID: " + str(line_qs.id)
                        )
                else:
                    list_of_error.append(
                        "Order Cannot be confirmed for Order Line ID: "
                        + str(line_qs.id)
                    )

            if len(list_of_error) > 0:
                return ResponseWrapper(error_msg=list_of_error, error_code=400, status=400)
            # order_qs = Order.objects.filter(id=order_id)
            if not order_qs.lines.filter(status="pending"):
                order_qs.status = "Confirm"
                order_qs.save()
            serializer = OrderDetailsSerializer(instance=order_qs)

            return ResponseWrapper(
                data=serializer.data, msg="Order Confirmed Successfully"
            )

        except Exception as e:
            return ResponseWrapper(error_msg=str(e), error_code=400, status=400)

    def order_line_update(self, request, *args, **kwargs):

        line_qs = Line.objects.filter(**kwargs).last()

        if not line_qs:
            return ResponseWrapper(error_msg="Order Line with this id not found.", error_code=400, status=400)
        else:
            quantity = request.data.get('quantity')
            if quantity<=0:
                return ResponseWrapper(error_msg="Please provide a valid quantity.", error_code=400, status=400)

            product_qs = Product.objects.filter(id=line_qs.product.id).last()
            if not product_qs:
                return ResponseWrapper(error_msg="Product not found.", error_code=400, status=400)

            stockrecord_qs = StockRecord.objects.filter(product_id=product_qs.id).first()
            if not stockrecord_qs:
                return ResponseWrapper(error_msg="Stockrecord of this product not found.", error_code=400, status=400)

            '''
            This condition will be true if the sum of the user's current quantity and 
            the quantity available in stock is greater than the new quantity.
            '''
            if (stockrecord_qs.num_in_stock+line_qs.quantity)>=quantity:
                if line_qs.quantity>quantity:
                    '''
                    If the user reduces the quantity from earlier 
                    then the reduced quantity will be added to the stock
                    '''
                    reduced_quantity = line_qs.quantity - quantity
                    new_stock = stockrecord_qs.num_in_stock + reduced_quantity
                    stockrecord_qs.num_in_stock=new_stock
                    stockrecord_qs.save()
                    line_qs.quantity=quantity
                    line_qs.save()
                elif line_qs.quantity<quantity:
                    '''
                    If the user increases the quantity from earlier 
                    then the newly added quantity will be removed from the stock
                    '''
                    added_quantity = quantity - line_qs.quantity
                    new_stock = stockrecord_qs.num_in_stock - added_quantity
                    stockrecord_qs.num_in_stock=new_stock
                    stockrecord_qs.save()
                    line_qs.quantity=quantity
                    line_qs.save()

                else:
                    return ResponseWrapper(error_msg="No change in quantity.", error_code=400, status=400)
                
                return ResponseWrapper(error_msg="Quantity updated successfully.", error_code=200, status=200)
            else:
                return ResponseWrapper(error_msg="Not enough stock of this product.", error_code=400, status=400)


class OrderLineUnavailableViewSet(viewsets.ModelViewSet):
    serializer_class = OrderLineSerializerIds

    def unavailable(self, request, *args, **kwargs):
        try:
            Line_ids = request.data.get('ids')
            list_of_error = []
            order_id = -9999

            for Line_id in Line_ids:
                Line_qs = Line.objects.get(id=Line_id)
                product_qs = Product.objects.get(id=Line_qs.product.id)
                partner_qs = Partner.objects.get(id=Line_qs.partner.id)

                if Line_qs.status == "unavailable":
                    list_of_error.append(
                        "Order Already unavailable for Order Line ID: "
                        + str(Line_qs.id)
                    )
                elif Line_qs.status == "Cancelled":
                    list_of_error.append(
                        "Order Already Cancelled for Order Line ID: " + str(Line_qs.id)
                    )
                elif Line_qs.status == "Pending":
                    try:
                        if (
                            partner_qs.partner_type.name == "Marketplace"
                            or partner_qs.partner_type.name == "Service"
                        ):
                            if product_qs.is_public:
                                if order_id == -9999 or order_id == Line_qs.order.id:
                                    Line_qs.status = "unavailable"
                                    Line_qs.save()
                                    order_id = Line_qs.order.id
                                    send_order_unavailable_notification.delay(
                                        str(order_id)
                                    )
                                else:
                                    list_of_error.append(
                                        "Order ID not matching for Order Line ID: "
                                        + str(Line_qs.id)
                                    )
                            else:
                                list_of_error.append(
                                    "Product Not Public for Order Line ID: "
                                    + str(Line_qs.id)
                                )
                        else:
                            list_of_error.append(
                                "Partner is not matching for Order Line ID: "
                                + str(Line_qs.id)
                            )
                    except Exception as e:
                        list_of_error.append(
                            str(e) + " for Order Line ID: " + str(Line_qs.id)
                        )
                else:
                    list_of_error.append(
                        "Order Cannot be unavailable for Order Line ID: "
                        + str(Line_qs.id)
                    )

            if len(list_of_error) > 0:
                return ResponseWrapper(error_msg=list_of_error, error_code=400, status=400)
            order_qs = Order.objects.get(id=order_id)
            order_qs.status = "unavailable"
            order_qs.save()

            return ResponseWrapper({"msg": "Order unavailable Successfully"})

        except Exception as e:
            return ResponseWrapper(error_msg=str(e), error_code=400, status=400)


class OrderLineDeliveredViewSet(viewsets.ModelViewSet):
    serializer_class = OrderLineSerializerIds

    def delivered(self, request, *args, **kwargs):
        try:
            Line_ids = request.data.get('order_item_id')
            list_of_error = []
            order_id = -9999

            for Line_id in Line_ids:
                Line_qs = Line.objects.get(id=Line_id)
                product_qs = Product.objects.get(id=Line_qs.product.id)
                partner_qs = Partner.objects.get(id=Line_qs.partner.id)

                if Line_qs.status == "Delivered":
                    list_of_error.append(
                        "Order Already Delivered for Order Line ID: " + str(Line_qs.id)
                    )
                elif Line_qs.status == "Cancelled":
                    list_of_error.append(
                        "Order Already Cancelled for Order Line ID: " + str(Line_qs.id)
                    )
                elif Line_qs.status == "Pending":
                    try:
                        if (
                            partner_qs.partner_type.name == "Marketplace"
                            or partner_qs.partner_type.name == "Service"
                        ):
                            if product_qs.is_public:
                                if order_id == -9999 or order_id == Line_qs.order.id:
                                    Line_qs.status = "Delivered"
                                    Line_qs.save()
                                    order_id = Line_qs.order.id
                                    send_order_delivered_notification.delay(
                                        str(order_id)
                                    )
                                else:
                                    list_of_error.append(
                                        "Order ID not matching for Order Line ID: "
                                        + str(Line_qs.id)
                                    )
                            else:
                                list_of_error.append(
                                    "Product Not Public for Order Line ID: "
                                    + str(Line_qs.id)
                                )
                        else:
                            list_of_error.append(
                                "Partner is not matching for Order Line ID: "
                                + str(Line_qs.id)
                            )
                    except Exception as e:
                        list_of_error.append(
                            str(e) + " for Order Line ID: " + str(Line_qs.id)
                        )
                else:
                    list_of_error.append(
                        "Order Cannot be Delivered for Order Line ID: "
                        + str(Line_qs.id)
                    )

            if len(list_of_error) > 0:
                return ResponseWrapper(error_msg=list_of_error, error_code=400, status=400)
            order_qs = Order.objects.get(id=order_id)
            order_qs.status = "Delivered"
            order_qs.save()

            return ResponseWrapper({"msg": "Order Delivered Successfully"})

        except Exception as e:
            return ResponseWrapper(error_msg=str(e), error_code=400, status=400)


class OrderCreateViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductsCustomSerializer
    """
    If you've got some options to configure for the product to add to the
    basket, you should pass the optional ``options`` property:
    {
        "url": "http://testserver.org/oscarapi/products/209/",
        "quantity": 6,
        "options": [{
            "option": "http://testserver.org/oscarapi/options/1/",
            "value": "some value"
        }]
    }
    """
    def generate_invoice_number(self, order):
        year_last_two_numbers = datetime.now().year % 100
        return '{}{:06d}'.format(year_last_two_numbers, order.id)  # E.g. "19000001'

    def discount_calculation(self, today, total_incl_tax, total_excl_tax, quantity, product_qs, cart):

        if product_qs.is_public:
            data = {}
            cart.add_product(
                product=product_qs,
                quantity=quantity,
            )
            if product_qs.discount:
                discount_valid = False
                if product_qs.discount.schedule_type == 'Time_Wise':
                    if product_qs.discount.start_time <= today.time() <= product_qs.discount.end_time:
                        discount_valid = True
                elif product_qs.discount.schedule_type == 'Date_Wise':
                    if product_qs.discount.start_date <= today.date() <= product_qs.discount.end_date:
                        discount_valid = True
                if discount_valid == True:
                    if product_qs.discount.discount_type == 'PERCENTAGE':
                        amount = float(product_qs.stockrecords.first().price) * float(product_qs.discount.amount) / 100
                        total_incl_tax = total_incl_tax + quantity * float(product_qs.stockrecords.first().price) - amount
                        total_excl_tax = total_excl_tax + quantity * float(product_qs.stockrecords.first().price) - amount
                    elif product_qs.discount.discount_type == 'AMOUNT':
                        amount = float(product_qs.discount.amount)
                        total_incl_tax = total_incl_tax + quantity * float(product_qs.stockrecords.first().price) - amount
                        total_excl_tax = total_excl_tax + quantity * float(product_qs.stockrecords.first().price) - amount
                else:
                    return ResponseWrapper(
                        error_msg='Product Discount is not valid',
                        error_code=400, status=400
                    )
            else:
                total_incl_tax = total_incl_tax + quantity * float(product_qs.stockrecords.first().price)
                total_excl_tax = total_excl_tax + quantity * float(product_qs.stockrecords.first().price)
            
            data['total_incl_tax'] = total_incl_tax
            data['total_excl_tax'] = total_excl_tax
            cart.save()
            return data

        else:
            return ResponseWrapper(
                error_msg='Product is not public for Product ID: ' + str(product_qs.id),
                error_code=400
            )

    def promotion_calculation(self, promo_code, total_incl_tax, total_excl_tax, today):
        data = {}
        promo_code_qs = PromoCode.objects.filter(code=promo_code).last()
        if promo_code_qs:
            promo_valid = False
            if promo_code_qs.schedule_type == 'Time_Wise':
                if promo_code_qs.start_time <= today.time() <= promo_code_qs.end_time:
                    promo_valid = True 
            elif promo_code_qs.schedule_type == 'Date_Wise':
                if promo_code_qs.start_date <= today.date() <= promo_code_qs.end_date:
                    promo_valid = True  
            if promo_valid:
                if promo_code_qs.promo_type == 'PERCENTAGE':
                    if promo_code_qs.minimum_purchase_amount <= total_excl_tax and promo_code_qs.max_purchase_amount >= total_excl_tax:
                        amount = (total_excl_tax * promo_code_qs.amount) / 100
                        total_excl_tax = total_excl_tax - amount
                        total_incl_tax = total_incl_tax - amount
                    else:
                        return ResponseWrapper(
                            error_msg='Promo Code is not valid for this order',
                            error_code=400, status=400
                        )
                elif promo_code_qs.promo_type == 'AMOUNT':
                    if promo_code_qs.minimum_purchase_amount <= total_excl_tax and promo_code_qs.max_purchase_amount >= total_excl_tax:
                        total_excl_tax = total_excl_tax - promo_code_qs.amount
                        total_incl_tax = total_incl_tax - promo_code_qs.amount  
                    else:
                        return ResponseWrapper(
                            error_msg='Promo Code is not valid for this order',
                            error_code=400, status=400
                        )
                else:
                    return ResponseWrapper(
                        error_msg='Promo Code is not valid for this order',
                        error_code=400, status=400
                    )
                data['total_incl_tax'] = total_incl_tax
                data['total_excl_tax'] = total_excl_tax
                return data
            else:
                return ResponseWrapper(
                    error_msg='Promo Code is not valid for this order',
                    error_code=400, status=400
                )
        else:
            return ResponseWrapper(
                error_msg='Promo Code is not valid for this order',
                error_code=400, status=400
            )
    
    def order_create(self, order_number, site, cart, user, partner_qs, order_count_per_schedule_qs, received_date, billing_address, shipping_address, shipping_method, status, total_incl_tax, total_excl_tax):
        order = Order.objects.create(
            number=order_number,
            site=site,
            basket=cart,
            user=user,
            zone = partner_qs.zone,
            order_count_per_schedule = order_count_per_schedule_qs,
            received_date = received_date,
            billing_address=billing_address,
            shipping_address=shipping_address,
            shipping_method=shipping_method,
            status=status,
            # guest_email=None,
            total_incl_tax=total_incl_tax,
            total_excl_tax=total_excl_tax,
            )
        if not order:
            return ResponseWrapper(
                error_msg='Order is not created',
                error_code=400, status=400
            )
        else:
            return order

    def order_line_create(self, order, product_qs, partner_qs, line_price_incl_tax, line_price_before_discounts_incl_tax, line_price_before_discounts_excl_tax, quantity):
        if product_qs.is_public:
            # check product stock record 
            stock = product_qs.stockrecords.first().num_in_stock

            if quantity <= stock and stock != 0:
                stockrecord = get_object_or_404(StockRecord, product_id=product_qs.id)
                stockrecord.num_in_stock = stock - quantity
                # stockrecord.save()
            else:
                return ResponseWrapper(error_msg="Low stock can not order", error_code=400, status=400)

            line = Line.objects.create(
                order=order,
                product=product_qs,
                partner=partner_qs,
                # partner_sku=product['partner_sku'],
                partner_sku=product_qs.stockrecords.first().partner_sku,
                title=product_qs.title,
                line_price_incl_tax=line_price_incl_tax,
                line_price_excl_tax=product_qs.stockrecords.first().price,
                line_price_before_discounts_incl_tax=line_price_before_discounts_incl_tax,
                line_price_before_discounts_excl_tax=line_price_before_discounts_excl_tax,
                # line_price_incl_tax=product['line_price_incl_tax'],
                # line_price_excl_tax=product['line_price_excl_tax'],
                # line_price_before_discounts_incl_tax=product['line_price_before_discounts_incl_tax'],
                # line_price_before_discounts_excl_tax=product['line_price_before_discounts_excl_tax'],
                quantity=quantity,
                status="Initialized",
            )
            if not line:
                return ResponseWrapper(
                    error_msg='Order Line is not created',
                    error_code=400, status=400
                )
            else:
                return line
        else:
            return ResponseWrapper(
                error_msg='Product is not public',
                error_code=400, status=400
            )

    def order_invoice(self, order):
        # create invoice
        number = self.generate_invoice_number(order)
        legal_entity = LegalEntity.objects.filter(id=1).first()
        invoice = Invoice.objects.create(
            number=number,
            order=order,
            legal_entity=legal_entity,
            notes=order.number,
            )
        if not invoice:
            return ResponseWrapper(
                error_msg='Invoice is not created',
                error_code=400, status=400
            )


    # still need to add previous order check, and product availability to buy, stock update, error msg and success msg
    def create(self, request, *args, **kwargs):
        today = datetime.today()
        today_second = today.time().second
        line_price_incl_tax = 0 # need to calculate after
        line_price_excl_tax = 0 # need to calculate after
        line_price_before_discounts_incl_tax = 0  # need to calculate after
        line_price_before_discounts_excl_tax = 0 # need to calculate after
        order_count_per_schedule = request.data.get('order_count_per_schedule')
        received_date = request.data.get('received_date') # Receive Date Format YYYY-MM-DD
        payment_type = request.data.get("payment_type")
        if order_count_per_schedule:
            order_count_per_schedule_qs = OrderCountPerSchedule.objects.filter(
                id=order_count_per_schedule
            ).last()
            if not order_count_per_schedule_qs:
                return ResponseWrapper(
                    error_msg="Order Count id is Not Found", error_code=400, status=400
                )
        try:
            success_msg = None
            user = User.objects.filter(id=request.user.id).last()
            site = Site.objects.all().last()
            billing_address = BillingAddress.objects.filter(id=request.data.get('billing_address')).last()
            shipping_address = ShippingAddress.objects.filter(id=request.data.get('shipping_address')).last()
            shipping_method = request.data.get('shipping_method')
            guest_email = request.data.get('guest_email')
            products = request.data.get('products')
            promo_code = request.data.get('promo_code')
            total_incl_tax = 0
            total_excl_tax = 0
            marketplace = False
            daily_needs = False
            service = False
            list_of_error = []
            orders = []
            try:
                cart = operations.get_basket(request)
                for product in products:
                    product_qs = Product.objects.filter(id=product['product']).first()
                    if not product_qs:
                        return ResponseWrapper(
                            error_msg='Product is not found for Product ID: ' + str(product['product']),
                            error_code=400, status=400
                        )
                    if not product_qs.stockrecords.first():
                        return ResponseWrapper(error_msg=str(product_qs.id) +' Product stock is not Available', error_code=400, status=400)
                    partner_qs = Partner.objects.filter(zone=product_qs.stockrecords.first().partner.zone).first()
                    if not partner_qs:
                        return ResponseWrapper(
                            error_msg='Partner is not found for Product ID: ' + str(product['product']),
                            error_code=400, status=400
                        )
                    if product_qs.categories.first().partner_type.name == 'Marketplace':
                        marketplace = True
                        data = self.discount_calculation(today, total_incl_tax, total_excl_tax, product,product_qs,cart)
                        total_incl_tax = data['total_incl_tax']
                        total_excl_tax = data['total_excl_tax']
                order_number = today_second + OrderNumberGenerator().order_number(cart)
                order_number = str(order_number) + 'M'
                if marketplace:
                    if promo_code:
                        data = self.promotion_calculation(promo_code, total_incl_tax, total_excl_tax, today)
                        total_incl_tax = data['total_incl_tax']
                        total_excl_tax = data['total_excl_tax']
                    if payment_type == "COD":
                        status = 'Placed'
                        order = self.order_create(order_number, site, cart, user, partner_qs, order_count_per_schedule_qs, received_date, billing_address, shipping_address, shipping_method, status, total_incl_tax, total_excl_tax)
                        orders.append(order)
                    elif payment_type == "ONLINE_BANK":
                        status = 'Pending'
                        order = self.order_create(order_number, site, cart, user, partner_qs, order_count_per_schedule_qs, received_date, billing_address, shipping_address, shipping_method, status, total_incl_tax, total_excl_tax)
                        orders.append(order)
                    else:
                        return ResponseWrapper(
                            error_msg='Payment Type is not valid',
                            error_code=400, status=400
                        )
                    success_msg = 'Marketplace Order Created'
                
                #create order lines
                for product in products:
                    product_qs = Product.objects.filter(id=product['product']).first()
                    if not product_qs:
                        return ResponseWrapper(
                            error_msg='Product is not found for Product ID: ' + str(product['product']),
                            error_code=400, status=400
                        )
                    if not product_qs.stockrecords.first():
                        return ResponseWrapper(error_msg=str(product_qs.id) + ' Product stock is not Available',
                                               error_code=400, status=400)

                    partner_qs = Partner.objects.filter(zone=product_qs.stockrecords.first().partner.zone).first()
                    if not partner_qs:
                        return ResponseWrapper(
                            error_msg='Partner is not found for Product ID: ' + str(product['product']),
                            error_code=400, status=400
                        )
                    if product_qs.categories.first().partner_type.name == 'Marketplace':
                        line = self.order_line_create(order, product_qs, partner_qs, line_price_incl_tax, line_price_before_discounts_incl_tax, line_price_before_discounts_excl_tax, product["quantity"])
            except Exception as e:
                return ResponseWrapper(
                    error_msg=str(e),
                    error_code=400, status=400
                )

            try:
                cart = operations.get_basket(request)
                for product in products:
                    product_qs = Product.objects.filter(id=product['product']).first()
                    if not product_qs:
                        return ResponseWrapper(
                            error_msg='Product is not found for Product ID: ' + str(product['product']),
                            error_code=400, status=400
                        )
                    if not product_qs.stockrecords.first():
                        return ResponseWrapper(error_msg=str(product_qs.id) + ' Product stock is not Available',
                                               error_code=400, status=400)

                    partner_qs = Partner.objects.filter(zone=product_qs.stockrecords.first().partner.zone).first()
                    if not partner_qs:
                        return ResponseWrapper(
                            error_msg='Partner is not found for Product ID: ' + str(product['product']),
                            error_code=400, status=400
                        )
                    if product_qs.categories.first().partner_type.name == 'Daily Needs':
                        daily_needs = True
                        data = self.discount_calculation(today, total_incl_tax, total_excl_tax, product,product_qs,cart)
                        total_incl_tax = data['total_incl_tax']
                        total_excl_tax = data['total_excl_tax']
                order_number = today_second + OrderNumberGenerator().order_number(cart)
                order_number = str(order_number) + 'D'
                #create order
                if daily_needs:
                    if promo_code:
                        data = self.promotion_calculation(promo_code, total_incl_tax, total_excl_tax, today)
                        total_incl_tax = data['total_incl_tax']
                        total_excl_tax = data['total_excl_tax']
                    if payment_type == "COD":
                        status = 'Placed'
                        order = self.order_create(order_number, site, cart, user, partner_qs, order_count_per_schedule_qs, received_date, billing_address, shipping_address, shipping_method, status, total_incl_tax, total_excl_tax)
                        orders.append(order)
                    elif payment_type == "ONLINE_BANK":
                        status = 'Pending'
                        order = self.order_create(order_number, site, cart, user, partner_qs, order_count_per_schedule_qs, received_date, billing_address, shipping_address, shipping_method, status, total_incl_tax, total_excl_tax)
                        orders.append(order)
                    else:
                        return ResponseWrapper(
                            error_msg='Payment Type is not valid',
                            error_code=400, status=400
                        )
                    success_msg = success_msg + ', Daily Needs Order Created'
                #create order lines
                for product in products:
                    product_qs = Product.objects.filter(id=product['product']).first()
                    if not product_qs:
                        return ResponseWrapper(
                            error_msg='Product is not found for Product ID: ' + str(product['product']),
                            error_code=400, status=400
                        )
                    if not product_qs.stockrecords.first():
                        return ResponseWrapper(error_msg=str(product_qs.id) + ' Product stock is not Available',
                                               error_code=400, status=400)

                    partner_qs = Partner.objects.filter(zone=product_qs.stockrecords.first().partner.zone).first()
                    if not partner_qs:
                        return ResponseWrapper(
                            error_msg='Partner is not found for Product ID: ' + str(product['product']),
                            error_code=400, status=400
                        )
                    if product_qs.categories.first().partner_type.name == 'Daily Needs':
                        if product_qs.is_public:
                            line = self.order_line_create(order, product_qs, partner_qs, line_price_incl_tax, line_price_before_discounts_incl_tax, line_price_before_discounts_excl_tax, product["quantity"])    
            except Exception as e:
                return ResponseWrapper(
                    error_msg=str(e),
                    error_code=400, status=400
                )

            try:
                cart = operations.get_basket(request)
                for product in products:
                    product_qs = Product.objects.filter(id=product['product']).first()
                    if not product_qs:
                        return ResponseWrapper(
                            error_msg='Product is not found for Product ID: ' + str(product['product']),
                            error_code=400, status=400
                        )
                    if not product_qs.stockrecords.first():
                        return ResponseWrapper(error_msg=str(product_qs.id) + ' Product stock is not Available',
                                               error_code=400, status=400)

                    partner_qs = Partner.objects.filter(zone=product_qs.stockrecords.first().partner.zone).first()
                    if not partner_qs:
                        return ResponseWrapper(
                            error_msg='Partner is not found for Product ID: ' + str(product['product']),
                            error_code=400, status=400
                        )
                    if product_qs.categories.first().partner_type.name == 'Service':
                        service = True
                        data = self.discount_calculation(today, total_incl_tax, total_excl_tax, product,product_qs,cart)
                        total_incl_tax = data['total_incl_tax']
                        total_excl_tax = data['total_excl_tax']

                order_number = today_second + OrderNumberGenerator().order_number(cart)
                order_number = str(order_number) + 'S'
                #create order
                if service:
                    if promo_code:
                        data = self.promotion_calculation(promo_code, total_incl_tax, total_excl_tax, today)
                        total_incl_tax = data['total_incl_tax']
                        total_excl_tax = data['total_excl_tax']
                    if payment_type == "COD":
                        status = 'Placed'
                        order = self.order_create(order_number, site, cart, user, partner_qs, order_count_per_schedule_qs, received_date, billing_address, shipping_address, shipping_method, status, total_incl_tax, total_excl_tax)
                        orders.append(order)
                    elif payment_type == "ONLINE_BANK":
                        status = 'Pending'
                        order = self.order_create(order_number, site, cart, user, partner_qs, order_count_per_schedule_qs, received_date, billing_address, shipping_address, shipping_method, status, total_incl_tax, total_excl_tax)
                        orders.append(order)
                    else:
                        return ResponseWrapper(
                            error_msg='Payment Type is not valid',
                            error_code=400, status=400
                        )
                    success_msg = success_msg + ', Service Order Created'
                #create order lines
                for product in products:
                    product_qs = Product.objects.filter(id=product['product']).first()
                    if not product_qs:
                        return ResponseWrapper(
                            error_msg='Product is not found for Product ID: ' + str(product['product']),
                            error_code=400, status=400
                        )
                    partner_qs = Partner.objects.filter(zone=product_qs.stockrecords.first().partner.zone).first()
                    if not partner_qs:
                        return ResponseWrapper(
                            error_msg='Partner is not found for Product ID: ' + str(product['product']),
                            error_code=400, status=400
                        )
                    if product_qs.categories.first().partner_type.name == 'Service':
                        if product_qs.is_public:
                            line = self.order_line_create(order, product_qs, partner_qs, line_price_incl_tax, line_price_before_discounts_incl_tax, line_price_before_discounts_excl_tax, product["quantity"])

            except Exception as e:
                return ResponseWrapper(
                    error_msg=str(e),
                    error_code=400, status=400
                )
            if len(orders) > 0:
                for temp_order in orders:
                    self.order_invoice(temp_order)
                serializer = OrderDetailsSerializer(orders, many=True)
                return ResponseWrapper(
                    msg=success_msg,
                    data=serializer.data
                )
            else:
                return ResponseWrapper(
                    error_msg = str(list_of_error),
                    error_code=400, status=400
                )
        except Exception as e:
            return ResponseWrapper(
                error_msg = str(e),
                error_code = 400, status=400
            )


    def single_order_create(self, request, *args, **kwargs):
        today = datetime.today()
        today_second = today.time().second
        line_price_incl_tax = 0
        line_price_excl_tax = 0
        total_incl_tax = 0
        total_excl_tax = 0
        line_price_before_discounts_incl_tax = 0
        line_price_before_discounts_excl_tax = 0
        try:
            user = User.objects.filter(id=request.user.id).first()
            if not user:
                return ResponseWrapper(
                    error_msg='User is not found',
                    error_code=400, status=400
                )
            site = Site.objects.filter(id=1).first()
            product = request.data.get('product')
            quantity = request.data.get('quantity')
            product_qs = Product.objects.filter(id=product).first()
            if not product_qs:
                return ResponseWrapper(
                    error_msg='Product is not found for Product ID: ' + str(product),
                    error_code=403, 
                    status=403
                )
            partner_qs = Partner.objects.filter(id=product_qs.stockrecords.last().partner.id).first()
            if not partner_qs:
                return ResponseWrapper(
                    error_msg='Partner is not found for Product ID: ' + str(product),
                    error_code=403, 
                    status=403
                )
            cart = operations.get_basket(request)
            # cart.add_product(product_qs, quantity=quantity)
            data = self.discount_calculation(today, total_incl_tax, total_excl_tax, quantity, product_qs, cart)
            total_incl_tax = data['total_incl_tax']
            total_excl_tax = data['total_excl_tax']                

            order = None
            order_qs = Order.objects.filter(user=user, status='Initialized')
            if order_qs:
                for temp_order in order_qs:
                    line_qs = Line.objects.filter(order=temp_order, partner=partner_qs)
                    if line_qs:
                        order = temp_order
                        order.total_incl_tax = float(order.total_incl_tax) + float(total_incl_tax)
                        order.total_excl_tax = float(order.total_excl_tax) + float(total_excl_tax)
                        order.save()
                        product_line_qs = Line.objects.filter(order=order, partner=partner_qs, product=product_qs).first()
                        if product_line_qs:
                            product_line_qs.quantity = product_line_qs.quantity + quantity
                            product_line_qs.line_price_incl_tax = float(product_line_qs.line_price_incl_tax) + float(line_price_incl_tax)
                            product_line_qs.line_price_excl_tax = float(product_line_qs.line_price_excl_tax) + float(line_price_excl_tax)
                            product_line_qs.line_price_before_discounts_incl_tax = float(product_line_qs.line_price_before_discounts_incl_tax) + float(line_price_before_discounts_incl_tax)
                            product_line_qs.line_price_before_discounts_excl_tax = float(product_line_qs.line_price_before_discounts_excl_tax) + float(line_price_before_discounts_excl_tax)
                            product_line_qs.save()
                        else:
                            line = self.order_line_create(order, product_qs, partner_qs, line_price_incl_tax, line_price_before_discounts_incl_tax, line_price_before_discounts_excl_tax, quantity)

                        break

            if not order:
                order_number = today_second + OrderNumberGenerator().order_number(cart)
                partner_type = partner_qs.partner_type.name
                order_number = str(order_number) + partner_type[0]
                order = self.order_create(
                    order_number=order_number, 
                    site=site, 
                    cart=cart, 
                    user=user, 
                    partner_qs=partner_qs, 
                    order_count_per_schedule_qs=None, 
                    received_date=None, 
                    billing_address=None, 
                    shipping_address=None, 
                    shipping_method="", 
                    status="Initialized", 
                    total_incl_tax=total_incl_tax, 
                    total_excl_tax=total_excl_tax
                )
                line = self.order_line_create(order, product_qs, partner_qs, line_price_incl_tax, line_price_before_discounts_incl_tax, line_price_before_discounts_excl_tax, quantity)
            serializer = OrderDetailsSerializer(order)
            return ResponseWrapper(
                msg='Order Created',
                data=serializer.data
            )
        except Exception as e:
            return ResponseWrapper(
                error_msg = str(e),
                error_code = 400, 
                status=400
            )
        

        

class OrderCountPerScheduleViewSet(CustomViewSet):
    serializer_class = OrderCountPerScheduleSerializer
    pagination_class = CustomPagination
    queryset = OrderCountPerSchedule.objects.all()
    lookup_field = "pk"
    filterset_class = OrderCountPerScheduleFilter
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_fields = ("is_active",)

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        serializer_class = self.get_serializer_class()
        page_qs = self.paginate_queryset(qs)
        serializer = serializer_class(instance=page_qs, many=True)
        paginated_data = self.get_paginated_response(serializer.data)
        return ResponseWrapper(data=paginated_data.data, msg="Success")

    def create(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        schedule = request.data.get('schedule')
        partner = request.data.get('partner')
        total_order = request.data.get('total_order')
        if not schedule:
            return ResponseWrapper(error_msg='Schedule Id is not given', error_code=400, status=400)
        if not partner:
            return ResponseWrapper(error_msg='Partner ID is not given', error_code=400, status=400)
        if int(total_order) < 0:
            return ResponseWrapper(error_msg='Order must be positive number', error_code=400, status=400)

        schedule_qs = Schedule.objects.filter(id=schedule).first()
        if not schedule_qs:
            return ResponseWrapper(error_msg='Schedule not found.', error_code=400, status=400)

        partner_qs = Partner.objects.filter(id=partner).first()
        if not partner_qs:
            return ResponseWrapper(error_msg='Partner not found.', error_code=400, status=400)

        order_count_per_schedule_qs = OrderCountPerSchedule.objects.filter(schedule=schedule_qs, partner=partner_qs).first()
        if order_count_per_schedule_qs:
            return ResponseWrapper(error_msg='Order Count Per Schedule already exists.', error_code=400, status=400)

        if serializer.is_valid():
            qs = serializer.save()
            return ResponseWrapper(data=serializer.data, msg='created', status=201)
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400, status=400)


    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        qs = self.get_queryset()

        object = qs.filter(pk = pk)
        if not object.exists():
            return ResponseWrapper(error_msg="Order Count Per Schedule not found", error_code=404, status=404)

        serializer = self.get_serializer(object.first())
        return ResponseWrapper(serializer.data)

    def update(self, request, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, partial=True)

        qs = self.queryset.filter(**kwargs)
        if not qs.exists():
            return ResponseWrapper(error_msg="Order Count Not Found", error_code=404, status=404)

        schedule_object =  OrderCountPerSchedule.objects.filter(**kwargs).first()

        schedule = request.data.get('schedule')
        if not schedule:
            schedule = schedule_object.schedule

        partner = request.data.get('partner')
        if not partner:
            partner = schedule_object.partner

        schedule_qs = OrderCountPerSchedule.objects.filter(schedule = schedule).last()
        if not schedule_qs:
            return ResponseWrapper(error_msg='Schedule not found.', error_code=404, status=404)

        partner_qs = OrderCountPerSchedule.objects.filter(partner = partner).last()
        if not partner_qs:
            return ResponseWrapper(error_msg='Partner not found.', error_code=404, status=404)
        
        # if not(schedule != schedule_object.schedule.id or partner != schedule_object.partner.id):
        if schedule_qs and schedule_qs.partner == partner_qs.partner:
                return ResponseWrapper(error_msg='Order Count Already Exist', error_code=400, status=400)

        if serializer.is_valid():
            qs = serializer.update(instance=self.get_object(
            ), validated_data=serializer.validated_data)
            serializer = self.serializer_class(instance=qs)
            return ResponseWrapper(data=serializer.data, msg="updated")
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400, status=400)


class OrderCancelViewSet(viewsets.ModelViewSet):
    serializer_class = OrderCancelSerializer
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"

    def create(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)

        if serializer.is_valid():
            order_number = serializer.validated_data.get("order_number", None)
            order_qs = get_object_or_404(Order, number__exact=order_number)
            if not order_qs:
                return ResponseWrapper(error_msg='Order is Not Found', error_code=400, status=400)

            for product_qs in order_qs.lines.all():
                stockrecord = get_object_or_404(StockRecord, product_id=product_qs.id)
                stockrecord.num_in_stock += product_qs.quantity
                stockrecord.save()

            order_qs.status = "Cancelled"
            order_qs.save()
            order_qs.lines.update(status="Cancelled")

            serializer = OrderDetailsSerializer(instance=order_qs)

            # send_order_cancel_notification.delay(order_qs.number)
            return ResponseWrapper(data=serializer.data, msg='Order Cancelled Successfully', status=200,)
        else:
            return Response(serializer.errors, error_code=400, status=400)

# Order Cancel by specific user
class OrderCancelByUserViewSet(viewsets.ModelViewSet):
    serializer_class = OrderCancelSerializer
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"

    def order_cancel(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        if serializer.is_valid():
            order_number = serializer.validated_data.get("order_number", None)
            order = Order.objects.filter(user=user).filter(number=order_number).first()
            if order and order.status == 'Pending':
                order.status== "Cancelled"
                order_serializer = OrderDetailsSerializer(order)
                return ResponseWrapper(data = order_serializer.data)
            else:
                return ResponseWrapper(data = 'Order can not be cancelled')
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400, status=400)




class OrderItemCancelViewSet(viewsets.ModelViewSet):
    serializer_class = OrderItemCancelSerializer
    queryset = Order.objects.all()
    lookup_field = "pk"

    def create(self, request, *args, **kwargs):
        # serializer_class = self.get_serializer_class()
        # serializer = serializer_class(data=request.data)
        #
        # if serializer.is_valid():
        # order_number = serializer.validated_data.get("order_number", None)
        order_item_id = request.data.get("order_item_id", None)
        line_qs = Line.objects.filter(id = order_item_id).last()
        if not line_qs:
            return ResponseWrapper(error_msg='Order Items id is not Valid',
                                   error_code=400, status=400)
        if line_qs.status == 'Cancelled':
            return ResponseWrapper(error_msg='Order Items is Already Cancel',
                                   error_code=400, status=400)

        order_qs = line_qs.order
        if order_qs == 'Cancelled':
            return ResponseWrapper(error_msg='Order is Already Cancel',
                                   error_code=400, status=400)

        # for item in items:
        #     order_line = get_object_or_404(order.lines, id=item.id)
        stockrecord = get_object_or_404(StockRecord, product_id=line_qs.product.id)
        stockrecord.num_in_stock += line_qs.quantity
        stockrecord.save()
        line_qs.set_status("Cancelled")
        # qs = order_qs.lines.filter(status = 'Cancelled')

        if not order_qs.lines.filter(status__in=["pending","Confirm"]):
            order_qs.status = "Cancelled"
            order_qs.save()

        serializer = OrderDetailsSerializer(instance=order_qs)
        return ResponseWrapper(data=serializer.data, msg='Order Item Cancel Successfully')



class OrderReorderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderCreateSerializer

    filterset_class = OrderDetailsFilter
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filterset_fields = ("status","zone")

    def order_reorder_create(self, request, *args, **kwargs):
        order_id = request.data.get("order_id")

        """whether any order exist at the given order id and user"""
        order_qs = Order.objects.filter(number=order_id, user=self.request.user).last()

        if not order_qs:
            return ResponseWrapper(error_msg="Order Not Found", error_code=400, status=400)

        """
        If any order found in the given order id and user
        """
        products = order_qs.lines.all()  # retrive the products of the previous order

        today = datetime.today()
        today_second = today.time().second
        site = Site.objects.all().last()
        user = User.objects.get(id=request.user.id)

        total_incl_tax = 0
        total_excl_tax = 0
        line_price_incl_tax = 0
        line_price_excl_tax = 0
        line_price_before_discounts_incl_tax = 0
        line_price_before_discounts_excl_tax = 0

        """Used For flag"""
        list_of_error = []
        order_has_product = False

        try:
            cart = operations.get_basket(request)

            """Adding valid products in the cart"""
            for product in products:
                product_qs = Product.objects.filter(id=product.product.id).last()
                partner_qs = Partner.objects.filter(
                    zone=product_qs.stockrecords.first().partner.zone
                ).first()

                """Is the product is still public then add to cart
                else dont include in cart"""
                if product_qs.is_public:
                    order_has_product = True
                    cart.add_product(
                        product=product_qs,
                        quantity=product.quantity,
                    )
                    total_incl_tax = total_incl_tax + product.quantity * float(
                        product_qs.stockrecords.first().price
                    )
                    total_excl_tax = total_excl_tax + product.quantity * float(
                        product_qs.stockrecords.first().price
                    )
                else:
                    list_of_error.append(
                        "Product Not Public for Product ID: " + str(product_qs.id)
                    )
            cart.save()

            order_number = today_second + OrderNumberGenerator().order_number(cart)

            """Checking the type of the order
            and adding type flag in order number"""
            if product_qs.categories.first().partner_type.name == "Marketplace":
                order_number = str(order_number) + "M"
            elif product_qs.categories.first().partner_type.name == "Daily Needs":
                order_number = str(order_number) + "D"
            else:
                order_number = str(order_number) + "S"

            """If previous order has any valid product till now then create Reorder"""
            if order_has_product:
                reorder = Order.objects.create(
                    number=order_number,
                    site=site,
                    basket=cart,
                    user=user,
                    zone=partner_qs.zone,
                    order_count_per_schedule=order_qs.order_count_per_schedule,
                    # received_date = received_date,
                    billing_address=order_qs.billing_address,  # taking address from previous order address
                    shipping_address=order_qs.shipping_address,
                    shipping_method=order_qs.shipping_method,
                    status="Pending",
                    # guest_email=None,
                    total_incl_tax=total_incl_tax,
                    total_excl_tax=total_excl_tax,
                )
                success_msg = "Reorder Created"

            """Adding valid products in the order line"""
            for product in products:
                product_qs = Product.objects.filter(id=product.product.id).last()
                partner_qs = Partner.objects.filter(
                    zone=product_qs.stockrecords.first().partner.zone
                ).first()

                if product_qs.is_public:
                    Line.objects.create(
                        order=reorder,
                        product=product_qs,
                        partner=partner_qs,
                        # partner_sku=product['partner_sku'],
                        partner_sku=product_qs.stockrecords.first().partner_sku,
                        title=product_qs.title,
                        line_price_incl_tax=line_price_incl_tax,
                        line_price_excl_tax=line_price_excl_tax,
                        line_price_before_discounts_incl_tax=line_price_before_discounts_incl_tax,
                        line_price_before_discounts_excl_tax=line_price_before_discounts_excl_tax,
                        # line_price_incl_tax=product['line_price_incl_tax'],
                        # line_price_excl_tax=product['line_price_excl_tax'],
                        # line_price_before_discounts_incl_tax=product['line_price_before_discounts_incl_tax'],
                        # line_price_before_discounts_excl_tax=product['line_price_before_discounts_excl_tax'],
                        # quantity=product['quantity'],
                        status="Pending",
                    )
                else:
                    list_of_error.append(
                        "Product Not Public for Product ID: " + str(product_qs.id)
                    )
        except Exception as e:
            list_of_error.append(str(e))

        serializer = OrderDetailsSerializer(instance=reorder)

        if reorder:
            return ResponseWrapper(
                msg=success_msg,
                data=serializer.data,
                # data = list_of_error,
            )
        else:
            return ResponseWrapper(
                msg=success_msg,
                data=list_of_error,
            )


    def order_details(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        employee_qs = Employee.objects.filter(user=user).first()

        if str(employee_qs.employee_category) == "Merchant" and employee_qs.is_active:
            order_no = kwargs.get("order_no")
            print("order_no", order_no)

            order_qs = Order.objects.filter(number=order_no).first()
            print("order_qs", order_qs)
            if order_qs:
                order_details = OrderDetailsByEmployeeSerializer(order_qs).data
                return ResponseWrapper(
                    msg="Order Details",
                    data=order_details,
                )
            else:
                return ResponseWrapper(error_msg="Order Not Found", error_code=400, status=400)
        else:
            return ResponseWrapper(error_msg="You are not authorized", error_code=400, status=400)


class StatusWiseOrderViewSet(CustomViewSet):
    serializer_class = OrderDetailsSerializer

    def get_queryset(self):
        queryset = Order.objects.all()
        zone = self.request.query_params.get("zone")
        if zone is not None:
            queryset = queryset.filter(zone__title__icontains=zone)
        return queryset

    def picked(self, request):
        qs = self.get_queryset()
        picked_order = qs.filter(status__iexact="Picked")
        page_qs = self.paginate_queryset(picked_order)
        serializer = self.get_serializer(page_qs, many=True)
        paginated_data = self.get_paginated_response(serializer.data)
        return ResponseWrapper(data=paginated_data.data, msg="Order Picked List")

    def on_the_way(self, request):
        qs = self.get_queryset()
        on_the_way_order = qs.filter(status__iexact="On the Way")
        page_qs = self.paginate_queryset(on_the_way_order)
        serializer = self.get_serializer(page_qs, many=True)
        paginated_data = self.get_paginated_response(serializer.data)
        return ResponseWrapper(data=paginated_data.data, msg="Order On the Way List")

    def delivered(self, request):
        qs = self.get_queryset()
        delivered_order = qs.filter(status__iexact="Delivered")
        page_qs = self.paginate_queryset(delivered_order)
        serializer = self.get_serializer(page_qs, many=True)
        paginated_data = self.get_paginated_response(serializer.data)
        return ResponseWrapper(data=paginated_data.data, msg="Order Delivered List")

class OrderPlacedSerializer(CustomViewSet):
    serializer_class = OrderPlaceSerializer
    queryset = Order.objects.all()

    def status_change(self, request):
        qs = self.get_queryset()
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        if serializer.is_valid():
            order_number = serializer.validated_data.get("order_number")

            # check for valid order number
            order = get_object_or_404(Order, number__exact=order_number)

            # change status to placed
            if order.status == "Pending":
                order.set_status("Placed")
                order.save()
            else:
                return ResponseWrapper(error_msg="Only pending order can update to placed", error_code=400, status=400)

            order_serializer = OrderDetailsSerializer(order)

            return ResponseWrapper(data=order_serializer.data, msg='Order Status change to Placed')
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400, status=400)
