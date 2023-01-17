from django.db import models
from oscar.apps.partner.abstract_models import AbstractPartner
from oscar.models.fields.slugfield import SlugField
from django.utils.translation import gettext_lazy as _
from django.contrib.gis.db import models as geo_models
from oscar.core.utils import slugify

class Zone(models.Model):
    title = models.CharField(max_length=150)
    location = geo_models.PolygonField(srid=4326, null=True,blank=True)
    address = models.CharField(max_length=100, default='Dhaka')
    city = models.CharField(max_length=50, default='Dhaka')
    is_active = models.BooleanField(default=True)
    # latitude = models.DecimalField(max_digits=22, decimal_places=16)
    # longitude = models.DecimalField(max_digits=22, decimal_places=16)

    def __str__(self):
        return self.title


class SubZone(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    area = geo_models.PolygonField(null=True,blank=True)
    zone = models.ForeignKey(
        Zone, on_delete=models.CASCADE, null=True, blank=True,
        related_name='sub_zones'
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class PartnerType(models.Model):
    name = models.CharField(max_length=50)
    slug = SlugField(_('Slug'), max_length=255, db_index=True)
    
    def __str__(self):
        return self.name
    def generate_slug(self):
        """
        Generates a slug for a category. This makes no attempt at generating
        a unique slug.
        """
        return slugify(self.name)

    def save(self, *args, **kwargs):
        """
        Oscar traditionally auto-generated slugs from names. As that is
        often convenient, we still do so if a slug is not supplied through
        other means. If you want to control slug creation, just create
        instances with a slug already set, or expose a field on the
        appropriate forms.
        """
        if not self.slug:
            self.slug = self.generate_slug()
        super().save(*args, **kwargs)

class Partner(AbstractPartner):
    GRADE = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('OTHERS', 'Others'),
    ]
    partner_type = models.ForeignKey(PartnerType, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='partners'
    )
    logo = models.ImageField(upload_to='logo', null=True, blank=True)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE,
                             related_name= 'partners',null=True,
                             blank=True)
    grade = models.CharField(choices=GRADE,
                                     max_length=50, default="OTHERS",
                                     null=True, blank=True)
    zip_code = models.CharField(max_length=10, null=True, blank=True)
    is_third_party_delivery = models.BooleanField(default=False)
    is_third_party_pickup = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


from oscar.apps.partner.models import *  # noqa isort:skip


