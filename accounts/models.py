from django.db import models
# from oscar.apps.address.abstract_models import AbstractUserAddress

from apps.partner.models import Zone, SubZone
from django.contrib.auth.models import AbstractUser, User
from django.contrib.gis.db import models as geo_models
from apps.partner.models import Partner

# Create your models here.


class UserAccount(AbstractUser):
    # username = None
    # phone = None
    # last_name = None

    phone = models.CharField(max_length=35, unique=True)
    is_block = models.BooleanField(default=False)
    # meta = models.JSONField(default=dict)

    # USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['email',"phone"]

    # def set_meta():


    class Meta:
        permissions = (
            ('custom_add_permission_useraccount', 'Custom can add permission useraccount'),
            ('custom_update_permission_useraccount', 'Custom can update permission useraccount'),
            ('custom_delete_permission_useraccount', 'Custom can delete permission useraccount'),
            ('custom_view_permission_useraccount', 'Custom can view permission useraccount'),
            ('custom_add_product', 'Custom can add product'),
            ('custom_update_product', 'Custom can update product'),
            ('custom_delete_product', 'Custom can delete product'),
            ('custom_view_all_product', 'Custom can view all product'),
            ('custom_update_product_category', 'Custom can update product category'),
            ('custom_delete_product_category', 'Custom can delete product category'),
            ('custom_add_product_sub_category', 'Custom can add product sub category'),
            ('custom_update_product_sub_category', 'Custom can update product sub category'),
            ('custom_delete_product_sub_category', 'Custom can delete product sub category'),
            ('custom_add_product_stock', 'Custom can add product stock'),
            ('custom_update_product_stock', 'Custom can update product stock'),
            ('custom_delete_product_stock', 'Custom can delete product stock'),
            ('custom_view_all_product_stock', 'Custom can view all product stock'),
            ('custom_view_all_order', 'Custom can view all order'),
            ('custom_view_all_order_item', 'Custom can view all order item'),
        #   ('custom_add_order', 'Custom can create new order'),
            ('custom_update_order', 'Custom can update order'),
            ('custom_update_order_item', 'Custom can update order item'),
            ('custom_view_order', 'Custom can view order'),
            ('custom_view_order_item', 'Custom can view order item'),
        #   ('custom_view_order_schedule', 'Custom can view order item'),
            ('custom_add_order_schedule', 'Custom can add order schedule'),
            ('custom_update_order_schedule', 'Custom can update order schedule'),
            ('custom_delete_order_schedule', 'Custom can delete order schedule'),
            ('custom_add_merchant', 'Custom can add merchant'),
            ('custom_update_merchant', 'Custom can update merchant'),
            ('custom_delete_merchant', 'Custom can delete merchant'),
            ('custom_block_merchant', 'Custom can block merchant'),
            ('custom_add_portfolio', 'Custom can add portfolio'),
            ('custom_update_portfolio', 'Custom can update portfolio'),
            ('custom_delete_portfolio', 'Custom can delete portfolio'),
            ('custom_add_employee', 'Custom can add employee'),
            ('custom_update_employee', 'Custom can update employee'),
            ('custom_delete_employee', 'Custom can delete employee'),
            ('custom_block_employee', 'Custom can block employee'),
            ('custom_add_partner', 'Custom can add partner'),
            ('custom_update_partner', 'Custom can update partner'),
            ('custom_delete_partner', 'Custom can delete partner'),
            ('custom_add_promo_code', 'Custom can add promo code'),
            ('custom_update_promo_code', 'Custom can update promo code'),
            ('custom_delete_promo_code', 'Custom can delete promo code'),
            ('custom_add_discount', 'Custom can add discount'),
            ('custom_update_discount', 'Custom can update discount'),
            ('custom_delete_discount', 'Custom can delete discount'),
            ('custom_add_customer', 'Custom can add customer'),
            ('custom_update_customer', 'Custom can update customer'),
            ('custom_delete_customer', 'Custom can delete customer'),
            ('custom_block_customer', 'Custom can block customer'),
            ('custom_add_notification', 'Custom can add notification'),
            ('custom_update_notification', 'Custom can update notification'),
            ('custom_delete_notification', 'Custom can delete notification'),
            ('custom_add_version', 'Custom can add version'),
            ('custom_update_version', 'Custom can update version'),
            ('custom_delete_version', 'Custom can delete version'),
            ('custom_delete_review', 'Custom can delete review'),
        )

        
    


class DeliveryMan(models.Model):
    sub_zone = models.ForeignKey(
        SubZone, on_delete=models.CASCADE, null=True, blank=True,
        related_name='delivery_mans'
    )
    current_location = geo_models.PolygonField(null=True, blank=True)
    user = models.OneToOneField(
        UserAccount, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='delivery_mans'
    )

class CustomerInfo(models.Model):
    GENDER = [
        ("MALE", "Male"),
        ("FEMALE", "Female"),
        ("OTHERS", "Others"),
        ]
    user = models.ForeignKey(
        to=UserAccount, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='customer_infos'
    )
    followed_store = models.ManyToManyField(
        to=Partner,
        null=True, blank=True, related_name='customer_infos'
    )

    gender = models.CharField(choices=GENDER,
                              default='MALE',max_length=20)

    image = models.FileField(upload_to='customer',
                             null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.user:
            return self.user.email
        else:
            return str(self.id)


class EmployeeCategory(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Employee(models.Model):
    STATUS = [
        ('PENDING', 'Pending'),
        ('ACCEPT', 'Accept'),
        ('REJECTED', 'Rejected'),
        ('BLOCKED', 'Blocked'),
    ]
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    employee_category = models.ForeignKey(EmployeeCategory, on_delete=models.CASCADE,
                                          null=True, blank=True, related_name='employees')
    nid = models.CharField(max_length=100, null=True, blank=True)

    image = models.ImageField(upload_to='employee',
                             null=True, blank=True)
    user = models.ForeignKey(
        to=UserAccount, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='employees'
    )
    shift_start_hour = models.TimeField(null=True, blank=True)
    shift_end_hour = models.TimeField(null=True, blank=True)
    phone = models.CharField(max_length=50)
    email = models.EmailField(max_length=150)
    date_of_birth = models.DateField(null=True, blank=True)
    # is_active = models.BooleanField(default=True)
    status = models.CharField(
        choices=STATUS, max_length=50, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# class UserAddress(AbstractUserAddress):
#     pass