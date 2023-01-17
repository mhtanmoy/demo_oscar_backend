from django.db import models
#from django.contrib.auth.models import User
from apps.partner.models import PartnerType
from oscar.apps.address.abstract_models import AbstractUserAddress
from oscar.apps.address.models import UserAddress

class CustomerAddress(UserAddress):
    partner_type = models.ManyToManyField(PartnerType, blank=True)

    class Meta:
        verbose_name = 'Customer User Address'
        verbose_name_plural = 'Customer User Addresses'

    def __str__(self):
        return self.first_name


class Version(models.Model):
    # version will be like 1.0.0 so float field is not suitable
    version = models.CharField(max_length=10)
    force_update = models.BooleanField(default=False)
    update_time = models.DateTimeField(auto_now=True)
    update_content = models.CharField(max_length=200)
    whatsnew = models.CharField(max_length=200)
    download_url = models.URLField(null=True, blank=True)
    is_customer_app = models.BooleanField(default=False)
    is_delivery_boy_app = models.BooleanField(default=False)
    is_android = models.BooleanField(default=False)
    is_ios = models.BooleanField(default=False)

    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    # device = models.CharField(max_length=50)

    # def save(self, *args, **kwargs):
    #     self.ios_version = round(self.ios_version, 3)

    def __str__(self):
        return self.version


# class AndroidVersion(models.Model):
#     # version will be like 1.0.0 so float field is not suitable
#     version = models.CharField(max_length=10)
#     update_time = models.DateTimeField(auto_now=True)
#     update_content = models.CharField(max_length=200)
#     whatsnew = models.CharField(max_length=200)
#     download_url = models.URLField(null=True, blank=True)
#     is_customer_app = models.BooleanField(default=False)
#     is_delivery_boy_app = models.BooleanField(default=False)
#     # user = models.ForeignKey(User, on_delete=models.CASCADE)
#     # device = models.CharField(max_length=50)



#     def save(self, *args, **kwargs):
#         self.android_version = round(self.android_version, 3)

#     def __str__(self):
#         return self.version 