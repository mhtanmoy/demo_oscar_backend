from django.db import models
from django.utils.translation import gettext_lazy as _
from oscar.apps.order.abstract_models import (AbstractOrder,
                                              AbstractLine)
from oscar.utils.models import get_image_upload_path
from apps.partner.models import Zone, Partner
from accounts.models import DeliveryMan
from oscar.apps.basket.models import Basket
from apps.catalogue.models import PromoCode


class Schedule(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return "Time Schedule " +str(self.start_time) +" - "+ str(self.end_time)


class OrderCountPerSchedule(models.Model):
    schedule = models.ForeignKey(
        Schedule, on_delete=models.CASCADE, related_name='order_count_per_schedules',
        null=True, blank=True
    )
    partner = models.ForeignKey(
        Partner, on_delete=models.CASCADE, related_name='order_count_per_schedules',
        null=True, blank=True
    )
    total_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.schedule)


class Order(AbstractOrder):
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE,
                             related_name= 'orders', null=True, blank=True)
    order_count_per_schedule = models.ForeignKey(
        OrderCountPerSchedule, on_delete=models.CASCADE,
        related_name='orders', null=True, blank=True
    )
    promo_code = models.ForeignKey(PromoCode, on_delete=models.CASCADE,
                             related_name= 'orders', null=True, blank=True)
    received_date = models.DateField(null=True, blank=True)


#     status = models.CharField(choices=ORDER_STATUS,
#                               default='ORDER_PLACED',
#                               max_length=50)
# #
#
# class Order(AbstractLine):
#     ORDER_STATUS = [
#         ("ORDER_PLACED", "User Confirm"),
#         ("ORDER_CONFIRM", "Order Confirm"),
#         ("PICKED", "Picked Up"),
#         ("ON_THE_WAY", "On the Way"),
#         ("DELIVERED", "Delivered"),
#         ("RETURNED", "Returned"),
#         ("CANCELLED", "Cancelled"),
#     ]
#     status = models.CharField(choices=ORDER_STATUS,
#                               default='ORDER_PLACED',
#                               max_length=50)

class OrderReturn(models.Model):
    RETURN_STATUS=[
        ('Pending','Pending'),
        ('ACCEPT','Accept'),
        ('REFUND','Refund'),
        ('CHANGE_PRODUCT','Change Product'),
        ('PARTNER_REJECTED', 'Partner Rejected'),
        ('ACCEPT','Accept'),
        ('SUCCESS','Success'),
    ]
    order = models.ForeignKey(Order,on_delete=models.CASCADE,
                              null=True, blank=True,related_name='order_returns')
    order_line = models.ManyToManyField('order.Line')
    return_counter = models.IntegerField(default=0)
    return_partner = models.ForeignKey(Partner,on_delete=models.CASCADE,
                                       null=True, blank=True,related_name='order_returns')
    return_status = models.CharField(max_length=100,choices=RETURN_STATUS,null=True,blank=True)


class OrderShippingEvent(models.Model):
    RETURN_STATUS = [
        ('SUCCESS', 'Success'),
        ('FAILED','Failed')
    ]
    delivery_man = models.ForeignKey(
        DeliveryMan, on_delete=models.CASCADE,
        null=True, blank=True,related_name='order_shipping_events'
    )
    return_partner = models.ForeignKey(
        Partner, on_delete=models.CASCADE,
        null=True, blank=True,related_name='order_shipping_events'
    )
    return_status = models.CharField(
        choices=RETURN_STATUS, max_length=25,
        default="SUCCESS")
    return_counter = models.IntegerField(default=0)
    return_log = models.JSONField(null=True, blank=True)


class ThirdPartyDelivery(models.Model):
    tracking_number = models.CharField(max_length=255)
    invoice_number = models.CharField(max_length=255)
    status = models.CharField(max_length=255) # Need to check
    others = models.JSONField()



from oscar.apps.order.models import *  # noqa isort:skip
