from asyncore import read
from dataclasses import field, fields
from .models import *
from rest_framework import serializers
from oscarapi.serializers.checkout import Country
from oscar.apps.order.models import Line
from oscar.apps.partner.models import StockRecord

from apps.catalogue.models import Category, Product
from apps.order.models import Order
from authentications.serializers import UserSerializerCustom
from customapp.serializers import *

class OrderCountPerScheduleSerializer(serializers.ModelSerializer):
    # partner_details = serializers.SerializerMethodField(read_only=True)
    # schedule_details = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = OrderCountPerSchedule
        fields = "__all__"

    # def get_partner_details(self, obj):
    #     if obj.partner:
    #         context = {
    #             'id': obj.partner.id,
    #             'code': obj.partner.code,
    #             'name': obj.partner.name,
    #             'partner_type': obj.partner.partner_type.name
    #         }
    #         return context
    #     return None
    # def get_schedule_details(self, obj):
    #     if obj.schedule:
    #         serializer = ScheduleSerializer(obj.schedule)
    #         return serializer.data
    #     return None

class BasketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Basket
        fields = '__all__'
class OrderlineSerializer(serializers.ModelSerializer):
    stockrecord = serializers.SerializerMethodField()

    class Meta:
        model = Line
        fields = '__all__'
    
    def get_stockrecord(self, obj):
        stockrecord = StockRecord.objects.filter(product_id=obj.product.id)
        if stockrecord.exists():
            stockrecord = stockrecord.first()
            return stockrecord.num_in_stock
        return None

class BillingAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = BillingAddress
        fields = '__all__'
from authentications.serializers import UserSerializerCustom

class ShippingAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShippingAddress
        fields = '__all__'

# ..........***.......... Category ..........***..........

class OrderDetailsSerializer(serializers.ModelSerializer):
    user = UserSerializerCustom(read_only=True)
    billing_address = serializers.SerializerMethodField(read_only=True)
    shipping_address = serializers.SerializerMethodField(read_only=True)
    order_count_per_schedule_details = serializers.SerializerMethodField(read_only=True)
    zone_details = serializers.SerializerMethodField(read_only=True)
    basket_details = serializers.SerializerMethodField(read_only=True)
    line_details = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = '__all__'

    def get_line_details(self, obj):
        if obj.lines:
            serializer = OrderlineSerializer(obj.lines, many=True)
            return serializer.data
        return None
    def get_billing_address(self, obj):
        if obj.billing_address:
            serializer = BillingAddressSerializer(obj.billing_address)
            return serializer.data
        return None
    def get_shipping_address(self, obj):
        if obj.shipping_address:
            serializer = ShippingAddressSerializer(obj.billing_address)
            return serializer.data
        return None
    def get_basket_details(self, obj):
        if obj.basket:
            serializer = BasketSerializer(obj.basket)
            return serializer.data
        return None
    def get_order_count_per_schedule_details(self, obj):
        if obj.order_count_per_schedule:
            serializer = OrderCountPerScheduleSerializer(obj.order_count_per_schedule)
            return serializer.data
        return None
    def get_zone_details(self, obj):
        if obj.zone:
            context = {
                'id': obj.zone.id,
                'title': obj.zone.title,
                # 'location': obj.zone.location,
                # 'address': obj.zone.address,
                # 'city': obj.zone.city
            }
            return context
        return None


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = "__all__"


class OrderCancelSerializer(serializers.Serializer):
    order_number = serializers.CharField(required=True)

class OrderNumberSerializer(serializers.Serializer):
    order_number = serializers.IntegerField(required=True)
class OrderItemSerializer(serializers.Serializer):
    order_item_id = serializers.PrimaryKeyRelatedField(many=True, required=True, queryset=Line.objects.all())


class OrderItemCancelSerializer(serializers.Serializer):
    # order_number = serializers.IntegerField(required=True)
    order_item_id = serializers.PrimaryKeyRelatedField(required=True, queryset=Line.objects.all())


# OrderCreateSerializer - body of request for creating order products (products, quantity, partner_name) and shipping address
class ProductsCustomSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField()

# class ProductsCustomOptionSerializer(serializers.Serializer):
#     product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
#     quantity = serializers.IntegerField()

PAYMENT_TYPE = (
    ("COD", "Cash On Delivery"),
    ("ONLINE_BANK", "Online Bank"),
)

class OrderCreateSerializer(serializers.Serializer):
    products = ProductsCustomSerializer(many=True)
    received_date =serializers.TimeField(required=False)
    order_count_per_schedule =serializers.IntegerField(required=False)
    billing_address = serializers.IntegerField()
    shipping_address = serializers.IntegerField()
    shipping_method = serializers.CharField()
    promo_code = serializers.CharField(required=False)
    payment_type = serializers.ChoiceField(choices=PAYMENT_TYPE)
    # guest_email = serializers.EmailField()

class OrderLineSerializerIds(serializers.Serializer):
    order_item_id = serializers.PrimaryKeyRelatedField(many=True, queryset=Product.objects.all())


class OrderListByEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class OrderDetailsByEmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializerCustom(read_only=True)
    billing_address = serializers.SerializerMethodField(read_only=True)
    shipping_address = serializers.SerializerMethodField(read_only=True)
    order_count_per_schedule_details = serializers.SerializerMethodField(read_only=True)
    zone_details = serializers.SerializerMethodField(read_only=True)
    basket_details = serializers.SerializerMethodField(read_only=True)
    line_details = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = '__all__'

    def get_line_details(self, obj):
        if obj.lines:
            serializer = OrderlineSerializer(obj.lines, many=True)
            return serializer.data
        return None
    def get_billing_address(self, obj):
        if obj.billing_address:
            serializer = BillingAddressSerializer(obj.billing_address)
            return serializer.data
        return None
    def get_shipping_address(self, obj):
        if obj.shipping_address:
            serializer = ShippingAddressSerializer(obj.billing_address)
            return serializer.data
        return None
    def get_basket_details(self, obj):
        if obj.basket:
            serializer = BasketSerializer(obj.basket)
            return serializer.data
        return None
    def get_order_count_per_schedule_details(self, obj):
        if obj.order_count_per_schedule:
            serializer = OrderCountPerScheduleSerializer(obj.order_count_per_schedule)
            return serializer.data
        return None
    def get_zone_details(self, obj):
        if obj.zone:
            context = {
                'id': obj.zone.id,
                'title': obj.zone.title,
                # 'location': obj.zone.location,
                # 'address': obj.zone.address,
                # 'city': obj.zone.city
            }
            return context
        return None



class OrderPlaceSerializer(serializers.Serializer):
    order_number = serializers.CharField(required=True)