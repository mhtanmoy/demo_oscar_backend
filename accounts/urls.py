from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()
router.register("accounts", AccountViewSet, basename="accounts")
# router.register("employee_category", EmployeeCategoryViewSet, basename="employee-category")
# router.register("employee", EmployeeViewSet, basename="employee")




urlpatterns =[
    path('employee_category/', EmployeeCategoryViewSet.as_view(
        {"get": "list", 'post':'create'}),
                      name="employee_category"),
    path('employee_category/<pk>/', EmployeeCategoryViewSet.as_view(
        {"patch": "update", 'delete':'destroy', 'get':'retrieve'}),
                      name="employee_category"),
    path('employee/', EmployeeViewSet.as_view(
        {"get": "list", 'post':'create'}),
                      name="employee"),
    path('employee/<pk>/', EmployeeViewSet.as_view(
        {"patch": "update", 'delete':'destroy', 'get':'retrieve'}),
                      name="employee"),
    path('merchant/', MerchantViewSet.as_view({"get": "list", 'post':'create'})),
    path('merchant/<int:pk>/', MerchantViewSet.as_view({"patch": "update", 'delete':'destroy', 'get':'retrieve'})),
    path("merchant/approve/<int:pk>/", MerchantViewSet.as_view({"patch": "approve"})),
    
 ] + router.urls