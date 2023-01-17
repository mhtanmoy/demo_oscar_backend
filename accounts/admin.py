from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(UserAccount)
admin.site.register(CustomerInfo)
admin.site.register(EmployeeCategory)
admin.site.register(Employee)