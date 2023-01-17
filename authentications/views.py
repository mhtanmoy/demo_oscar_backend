from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import generics, status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from utils.response_wrapper import ResponseWrapper
from oscar.apps.customer.signals import user_registered
from oscar.core.loading import get_class, get_model

from oscarapi.utils.session import login_and_upgrade_session
from oscarapi.utils.loading import get_api_classes
from oscarapi.basket import operations
from authentications.serializers import *

from django.core.mail import BadHeaderError, send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q
from utils.custom_viewset import CustomViewSet

from accounts.models import UserAccount as User
from accounts.models import CustomerInfo
from apps.partner.models import Partner
from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import Group, Permission
from utils.permissions import CheckCustomPermission
from accounts.models import Employee, EmployeeCategory
from accounts.serializers import EmployeeSerializer, EmployeeCategorySerializer
import re


class RegistrationView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        # if not getattr(settings, "OSCARAPI_ENABLE_REGISTRATION", False):
        #     return Response("Unauthorized", status=status.HTTP_401_UNAUTHORIZED)
        try:
            email = request.data['email']
            password = request.data['password']
            phone = request.data['phone']
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            if email:
                username = email
            else:
                username = phone

            if User.objects.filter(email=email).exists():
                return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)
            elif User.objects.filter(phone=phone).exists():
                return Response({"error": "Phone already exists"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                if email and password and phone and first_name and last_name:
                    user = User.objects.create_user(email=email, password=password, phone=phone, first_name=first_name, last_name=last_name, username=username)
                    user.save()
                    try:
                        send_mail(
                            'Registration Completed!',
                            'Thank you for registration!!! Welcome to Amarshohor',
                            [user.email],
                            fail_silently= False,
                        )
                    except:
                        print("An exception occurred To send Email")
                    if user:
                        return ResponseWrapper(data=LoginSerializer(user).data, msg="User created successfully", status=status.HTTP_201_CREATED)
                    else:
                        return ResponseWrapper(data=None, msg="User not created", status=status.HTTP_400_BAD_REQUEST)
                else:
                    return ResponseWrapper(
                        msg="Please provide Required fields",
                        status=status.HTTP_400_BAD_REQUEST
                    )
        except Exception as e:
            return ResponseWrapper(
                msg="Something went wrong, Please provide Required fields",
                status=status.HTTP_400_BAD_REQUEST
            )
        

class LoginView(generics.CreateAPIView):
    serializer_class = LoginSerializerCustom

    def post(self, request, *args, **kwargs):
        try:
            username = request.data.get('username', None)
            password = request.data.get('password', None)
            
            userdetail = User.objects.filter(Q(email=username) | Q(phone=username)).first()
            try:
                user = User.objects.get(email=userdetail)
            except:
                user = User.objects.get(phone=userdetail)
            if user is not None:
                if user.check_password(password):
                    

                    
                    return ResponseWrapper(
                        LoginSerializer(user).data,
                    )
                else:
                    return ResponseWrapper(
                        error_msg="Email or password is incorrect",
                        response_success=False,
                        status=400,
                    )
            else:
                return ResponseWrapper(
                    status=status.HTTP_400_BAD_REQUEST,
                    error_msg="User not found",
                    data=None,
                )
        except Exception as e:
            print(e)
            return ResponseWrapper(
                status=status.HTTP_400_BAD_REQUEST,
                error_msg="Something went wrong",
                data=None,
            )
        
class UserDetail(generics.ListAPIView):
    serializer_class = UserSerializerCustom
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            user = User.objects.filter(id=request.user.id).first()
            if user is not None:
                
                # customer_info = CustomerInfo.objects.filter(user=user).first()
                # if customer_info is not None:
                #     user.customer_info = customer_info
                # else:
                #     user.customer_info = None
                return ResponseWrapper(
                    data=UserSerializerCustom(user).data,
                    msg="User found",
                    status=status.HTTP_200_OK,
                )
            else:
                return ResponseWrapper(
                    status=status.HTTP_400_BAD_REQUEST,
                    msg="User not found",
                )
        except:
            return ResponseWrapper(
                status=status.HTTP_400_BAD_REQUEST,
                msg="User not found",
            )

    
class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    queryset = User.objects.all()
    lookup_field = 'pk'

    def patch(self, request, *args, **kwargs):
        try:
            username = request.data.get('username', None)
            user = User.objects.filter(Q(email=username) | Q(phone=username)).first()
            if user is not None:
                old_password = request.data.get('old_password', None)
                new_password = request.data.get('new_password', None)
                if user.check_password(old_password):
                    user.set_password(new_password)
                    user.save()
                    return ResponseWrapper(
                        LoginSerializer(user).data,
                        msg="Password changed successfully",
                        status=status.HTTP_200_OK,
                    )
                else:
                    return ResponseWrapper(
                        msg="Old password is incorrect",
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                return ResponseWrapper(
                    status=status.HTTP_400_BAD_REQUEST,
                    msg="User not found",
                )
        except:
            return ResponseWrapper(
                status=status.HTTP_400_BAD_REQUEST,
                msg="Something went wrong",
            )


class UpdateProfileView(CustomViewSet):
    serializer_class = UserSerializerCustom
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id).first()

    def update(self, request, *args, **kwargs):
        try:
            user = User.objects.filter(id=request.user.id).first()
            if user is not None:
                try:
                    image = request.FILES.get('image', None)
                    if image is not None:
                        customer_info = CustomerInfo.objects.filter(user=user).first()
                        if customer_info is not None:
                            customer_info.image = image
                        else:
                            customer_info = CustomerInfo.objects.create(
                                user=user,
                                image=image,
                            )
                        customer_info.save()
                except Exception as e:
                    print(e)
                serializer = UserSerializerCustom(user, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return ResponseWrapper(
                        data=serializer.data,
                        msg="Profile updated successfully",
                        status=status.HTTP_200_OK,
                    )
                else:
                    return ResponseWrapper(
                        status=status.HTTP_400_BAD_REQUEST,
                        msg="Something went wrong",
                    )
            else:
                return ResponseWrapper(
                    status=status.HTTP_400_BAD_REQUEST,
                    msg="User not found",
                )
        except Exception as e:
            return ResponseWrapper(
                error_msg=str(e),
                status=status.HTTP_400_BAD_REQUEST,
            )


class FollowCustomerInfoView(CustomViewSet):
    serializer_class = FollowedStoreSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        return CustomerInfo.objects.filter(user=self.request.user.id).first()

    def customer_store_follow(self, request, *args, **kwargs):
        store_id = request.data.get('partner_id')
        if not store_id:
            return ResponseWrapper(
                msg='Store id is required',
                error_code=400,
                status=400,
            )

        partner_qs = Partner.objects.filter(id=store_id).first()
        if not partner_qs:
            return ResponseWrapper(
                msg='Store id is not valid',
                error_code=400,
                status=400,
            )
        if not partner_qs.partner_type.name == 'Marketplace':
            return ResponseWrapper(
                msg='Store id is not valid',
                error_code=400,
                status=400,
            )
        customer_info_qs = CustomerInfo.objects.filter(user=request.user.id).first()
        if not customer_info_qs:
            customer_info = CustomerInfo.objects.create(
                user=request.user
            )
            customer_info.followed_store.add(partner_qs)
            customer_info.save()

        is_already_exist = customer_info_qs.followed_store.filter(id=store_id).first()
        if is_already_exist is None:
                customer_info_qs.followed_store.add(partner_qs)

                serializer = UserSerializerCustom(request.user)
                return ResponseWrapper(
                    data=serializer.data,
                    msg="Store Followed successfully",
                    status=200,
                )
        else:
            return ResponseWrapper(
                msg='Store already followed',
                error_code=400,
                status=400,
            )

    def customer_store_unfollow(self, request, *args, **kwargs):
        store_id = request.data.get('partner_id')
        if not store_id:
            return ResponseWrapper(
                msg='Store id is required',
                error_code=400,
                status=400,
            )

        partner_qs = Partner.objects.filter(id=store_id).first()
        if not partner_qs:
            return ResponseWrapper(
                msg='Store id is not valid',
                error_code=400,
                status=400,
            )
        if not partner_qs.partner_type.name == 'Marketplace':
            return ResponseWrapper(
                msg='Store id is not valid',
                error_code=400,
                status=400,
            )
        customer_info_qs = CustomerInfo.objects.filter(user=request.user.id).first()
        if not customer_info_qs:
            return ResponseWrapper(
                msg='User not found',
                error_code=400,
                status=400,
            )

        is_already_exist = customer_info_qs.followed_store.filter(id=store_id).first()
        if is_already_exist is not None:
                customer_info_qs.followed_store.remove(partner_qs)

                serializer = UserSerializerCustom(request.user)
                return ResponseWrapper(
                    data=serializer.data,
                    msg="Store Unfollowed successfully",
                    status=200,
                )
        else:
            return ResponseWrapper(
                msg='Store already unfollowed',
                error_code=400,
                status=400,
            )



class BlockUserView(CustomViewSet):
    serializer_class = BlockUserSerializer
    permission_classes = (IsAdminUser,)
    queryset = User.objects.all()

    def update(self, request, *args, **kwargs):
        try:
            user = request.data.get('user', None)
            if user is not None:
                user = User.objects.filter(id=user).first()
                if user is not None:
                    user.is_block = not user.is_block
                    user.save()
                    return ResponseWrapper(
                        data=UserSerializerCustom(user).data,
                        msg="User blocked status change successfully",
                        status=status.HTTP_200_OK,
                    )
                else:
                    return ResponseWrapper(
                        status=status.HTTP_400_BAD_REQUEST,
                        msg="User not found",
                    )
            else:
                return ResponseWrapper(
                    status=status.HTTP_400_BAD_REQUEST,
                    msg="User filed is empty",
                )
        except Exception as e:
            return ResponseWrapper(
                error_msg=str(e),
                status=status.HTTP_400_BAD_REQUEST,
            )





class ForgotPasswordView(generics.CreateAPIView):
    serializer_class = ForgotPasswordSerializer

    def post(self, request, *args, **kwargs):
        try:
            username = request.data.get('username', None)
            user = User.objects.filter(Q(email=username) | Q(phone=username)).first()
            if user is not None:
                new_password = request.data.get('new_password', None)
                user.set_password(new_password)
                user.save()
                return ResponseWrapper(
                    LoginSerializer(user).data,
                    msg="Password changed successfully",
                    status=status.HTTP_200_OK,
                )
            else:
                return ResponseWrapper(
                    status=status.HTTP_400_BAD_REQUEST,
                    msg="User not found",
                )
        except:
            return ResponseWrapper(
                status=status.HTTP_400_BAD_REQUEST,
                msg="User not found",
            )

class AllPermissionsView(CustomViewSet):
    serializer_class = PermissionSerializer

    def get_queryset(self):
        return Permission.objects.filter(name__istartswith='Custom')
        #return Permission.objects.all()

    def list(self, request, *args, **kwargs):
        try:
            permissions = self.get_queryset()
            serializer = PermissionSerializer(permissions, many=True)
            return ResponseWrapper(
                data=serializer.data,
                msg="Permissions",
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return ResponseWrapper(
                error_msg=str(e),
                status=status.HTTP_400_BAD_REQUEST,
            )



class PermissionsView(CustomViewSet):
    serializer_class = PermissionAddSerializer
    queryset = Permission.objects.all()
    #permission_classes = [(CheckCustomPermission("custom_add_permission_useraccount") | IsAdmin) & IsOwner]

    # user_permissions have defferent serializer class
    def get_serializer_class(self):
        if self.action == 'user_permissions':
            return UserPermissionSerializer
        return self.serializer_class

    def user_permissions(self, request, *args, **kwargs):
        try:
            user_id = request.data.get('user', None)
            user = User.objects.filter(id=user_id).last()
            if user is not None:
                permissions = user.user_permissions.all()
                serializer = PermissionSerializer(permissions, many=True)
                return ResponseWrapper(
                    data=serializer.data,
                    msg="Permissions",
                    status=status.HTTP_200_OK,
                )
            else:
                return ResponseWrapper(
                    msg="User not found",
                    error_code=404,
                    status=404,
                )
        except Exception as e:
            return ResponseWrapper(
                error_msg=str(e),
                status=status.HTTP_400_BAD_REQUEST,
            )



    def add_user_permission(self, request, *args, **kwargs):
        try:
            user_id = request.data.get('user', None)
            user = User.objects.filter(id=user_id).last()
            if user is not None:
                permissions = request.data.get('permissions', None)
                if permissions is not None:
                    for permission in permissions:
                        permission = Permission.objects.filter(id=permission).first()
                        if permission is not None:
                            user.user_permissions.add(permission)
                        else:
                            return ResponseWrapper(
                                status=status.HTTP_400_BAD_REQUEST,
                                msg="Permission not found",
                            )
                    user.save()
                    return ResponseWrapper(
                        data=UserSerializerCustom(user).data,
                        msg="Permission added successfully",
                        status=status.HTTP_200_OK,
                    )
                else:
                    return ResponseWrapper(
                        status=status.HTTP_400_BAD_REQUEST,
                        msg="Permission not found",
                    )
            else:
                return ResponseWrapper(
                    status=status.HTTP_400_BAD_REQUEST,
                    msg="User not found",
                )
        except Exception as e:
            return ResponseWrapper(
                error_msg=str(e),
                status=status.HTTP_400_BAD_REQUEST,
            )

    def remove_user_permission(self, request, *args, **kwargs):
        try:
            user_id = request.data.get('user', None)
            user = User.objects.filter(id=user_id).last()
            if user is not None:
                permissions = request.data.get('permissions', None)
                if permissions is not None:
                    for permission in permissions:
                        permission = Permission.objects.filter(id=permission).first()
                        if permission is not None:
                            user.user_permissions.remove(permission)
                        else:
                            return ResponseWrapper(
                                status=status.HTTP_400_BAD_REQUEST,
                                msg="Permission not found",
                            )
                    user.save()
                    return ResponseWrapper(
                        data=UserSerializerCustom(user).data,
                        msg="Permission removed successfully",
                        status=status.HTTP_200_OK,
                    )
                else:
                    return ResponseWrapper(
                        status=status.HTTP_400_BAD_REQUEST,
                        msg="Permission not found",
                    )
            else:
                return ResponseWrapper(
                    status=status.HTTP_400_BAD_REQUEST,
                    msg="User not found",
                )
        except Exception as e:
            return ResponseWrapper(
                error_msg=str(e),
                status=status.HTTP_400_BAD_REQUEST,
            )


class GroupView(CustomViewSet):
    serializer_class = GroupCustomSerializer
    queryset = Group.objects.all()

    def create(self, request, *args, **kwargs):
        group_name = request.data.get('name', None)
        permissions = request.data.get('permissions', None)
        if group_name is not None:
            group, created = Group.objects.get_or_create(name=group_name)
            if permissions is not None:
                for permission in permissions:
                    permission = Permission.objects.filter(id=permission).first()
                    if permission is not None:
                        group.permissions.add(permission)
                group.save()

            if group is not None:
                employeecategory, created = EmployeeCategory.objects.get_or_create(name=group_name)

                if employeecategory is not None:
                    msg = "Employee Category created successfully"

            return ResponseWrapper(
                data=GroupSerializer(group).data,
                msg=msg,
                status=200,
            )
        else:
            return ResponseWrapper(
                status=status.HTTP_400_BAD_REQUEST,
                msg="name is required",
            )

                
class EmployeeViewSet(CustomViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    lookup_field = "pk"

    # def get_permissions(self):
    #     if self.action == "create":
    #         permission_classes = [IsAuthenticated]
    #     else:
    #         permission_classes = [AllowAny]
    #     return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        employee_category = request.data.get("employee_category", None)
        try:
            if serializer.is_valid():
                first_name = serializer.validated_data.get("first_name")
                last_name = serializer.validated_data.get("last_name")
                email = serializer.validated_data.get("email")
                phone = serializer.validated_data.get("phone")
                password = serializer.validated_data.pop("password")
                group = None

                if employee_category is not None:
                    employeecategory = EmployeeCategory.objects.filter(id=employee_category).first()
                    if employeecategory is not None:
                        group = Group.objects.filter(name=employeecategory.name).first()
                        

                pattern = re.compile(r"[A-Za-z0-9-_]+")
                if not pattern.match(first_name):
                    return ResponseWrapper(
                        msg="Please Insert valid First Name",
                        error_code=400,
                        status=400
                    )
                if not pattern.match(last_name):
                    return ResponseWrapper(
                        msg="Please Insert valid Last Name",
                        error_code=400,
                        status=400
                    )

                existing_user = User.objects.filter(
                    Q(email__exact=email) | Q(phone__exact=phone)
                ).exists()
                if existing_user:
                    return ResponseWrapper(
                        msg="User already exists",
                        error_code=400,
                        status=400
                    )

                # Creating User
                new_user = User.objects.create_user(
                    username=email,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone=phone,
                    password=password,
                )
                # Assigning Group to User
                if group is not None:
                    new_user.groups.add(group)
                    # group permissions add to user permissions
                    for permission in group.permissions.all():
                        new_user.user_permissions.add(permission)
                    new_user.save()

                serializer.save(user=new_user)
                return ResponseWrapper(
                    data=serializer.data,
                    msg="Employee created successfully",
                    status=200,
                )
            else:
                return ResponseWrapper(
                    msg=serializer.errors,
                    error_code=400,
                    status=400
                )

        except Exception as e:
            return ResponseWrapper(
                msg=str(e),
                error_code=400,
                status=400
            )



