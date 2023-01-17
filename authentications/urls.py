from django.urls import path
from .views import *

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('user/', UserDetail.as_view(), name='user'),
    path('forgot_password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('change_password/', ChangePasswordView.as_view(), name='change-password'),
    path('block_user/', BlockUserView.as_view({"post": "update"}), name='block-user'),
    
    path('customer/register/', RegistrationView.as_view(), name='register'),
    path('customer/update_profile/', UpdateProfileView.as_view({"patch": "update"}), name='update-profile'),
    path('customer_store_follow/', FollowCustomerInfoView.as_view({"post": "customer_store_follow", "patch": "customer_store_unfollow"}), name='customer_store_follow'),

    path('permission/', PermissionsView.as_view({"post": "add_user_permission", "patch": "remove_user_permission"}), name='permissions'),
    path('user_permission/', PermissionsView.as_view({"post": "user_permissions"}), name='user_permissions'),
    path('all_permission/', AllPermissionsView.as_view({"get": "list"}), name='all_permissions'),

    path('role/', GroupView.as_view({"post": "create"}), name='group'),
    path('user_role/', EmployeeViewSet.as_view({"get": "list", "post": "create"}), name='employee'),
    
]