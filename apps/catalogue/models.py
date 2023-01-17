from django.db import models
from django.utils.translation import gettext_lazy as _
from oscar.apps.catalogue.abstract_models import AbstractProduct, AbstractCategory
from oscar.utils.models import get_image_upload_path
from apps.partner.models import Zone, PartnerType


class Discount(models.Model):
    DISCOUNT_SCHEDULE_TYPE = [("Time_Wise", "Time wise"), ("Date_Wise", "Date wise")]
    DISCOUNT_TYPE = [("PERCENTAGE", "Percentage"), ("AMOUNT", "Amount")]

    title = models.CharField(max_length=250)
    image = models.ImageField(upload_to="Offer", null=True, blank=True)
    schedule_type = models.CharField(
        choices=DISCOUNT_SCHEDULE_TYPE,
        max_length=50,
        default="Date_wise",
        null=True,
        blank=True,
    )
    discount_type = models.CharField(
        choices=DISCOUNT_TYPE,
        max_length=50,
        default="PERCENTAGE",
        null=True,
        blank=True,
    )
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    amount = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_schedule_type(self):
        if self.schedule_type == "Time_Wise":
            return "Time Wise"
        else:
            return "Date Wise"

    def get_discount_type(self):
        if self.schedule_type == "PERCENTAGE":
            return "Percentage"
        else:
            return "Amount"


# ............***............ Promo Code ............***............


class PromoCode(models.Model):
    PROMO_TYPE = [("PERCENTAGE", "percentage"), ("AMOUNT", "amount")]
    SCHEDULE_TYPE = [("Time_Wise", "Time wise"), ("Date_Wise", "Date wise")]
    code = models.CharField(max_length=200, unique=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    schedule_type = models.CharField(
        choices=SCHEDULE_TYPE, max_length=50, null=True, blank=True
    )
    promo_type = models.CharField(
        choices=PROMO_TYPE, max_length=50, null=True, blank=True
    )
    max_purchase_amount = models.FloatField(default=0)
    minimum_purchase_amount = models.FloatField(default=0)
    maximum_applied = models.IntegerField(default=0)
    amount = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code


class Product(AbstractProduct):
    short_description = models.TextField(_("Short Description"), blank=True)
    index = models.IntegerField(default=0, blank=True)
    unit = models.CharField(max_length=25, blank=True, null=True)
    discount = models.ForeignKey(
        Discount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    is_recommended = models.BooleanField(default=False)

    class Meta:
        ordering = ("index",)


class Category(AbstractCategory):
    thumbnail_image = models.ImageField(
        upload_to=get_image_upload_path, max_length=255, blank=True, null=True
    )

    partner_type = models.ForeignKey(
        PartnerType,
        on_delete=models.CASCADE,
        related_name="categorys",
        null=True,
        blank=True,
    )
    discount = models.ForeignKey(
        Discount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="categorys",
    )


from oscar.apps.catalogue.models import *  # noqa isort:skip
