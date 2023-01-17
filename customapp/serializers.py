from apps.extension.serializers import CustomCountrySerializer
from customapp.models import Version, CustomerAddress
from rest_framework import serializers
from oscar.core.loading import get_class, get_model
#from oscar.apps.address.models import UserAddress
from authentications.serializers import UserSerializerCustom
from accounts.models import UserAccount as User
from oscar.apps.order.models import ShippingAddress, BillingAddress
from oscarapi.serializers.checkout import Country
from drf_extra_fields.fields import Base64FileField, Base64ImageField

ProductImage = get_model('catalogue', 'ProductImage')
Product = get_model('catalogue', 'Product')
StockRecord = get_model('partner', 'StockRecord')
ProductReview = get_model('reviews', 'ProductReview')

class VersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Version
        fields = '__all__'

# class VersionSpecificSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Version
#         fields = '__all__'
#         read_only_fields = ('id', 'update_time', 'version')
    


class CustomProductImageSerializer(serializers.ModelSerializer):
    # product_id = serializers.SerializerMethodField(read_only = True)
    original = Base64ImageField()
    class Meta:
        model = ProductImage
        #depth = 1
        fields = '__all__'
        #read_only_fields = ['product']

    def create(self, validated_data):
        original = validated_data.pop('original', None)
        if original:
            return ProductImage.objects.create(original=original, **validated_data)
        return ProductImage.objects.create(**validated_data)

    # def get_product_id(self,obj):
    #     if obj.product:
    #         return obj.product.id
    #     return None

class StockRecordSerializerCustom(serializers.ModelSerializer):
    class Meta:
        model = StockRecord
        fields = '__all__'

class ProductReviewSerializerCustom(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = '__all__'
        read_only_fields = ['name','email','homepage','status','total_votes','delta_votes','product', 'user']

class ProductReviewSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = ['title', 'score', 'body']

class CustomUserAddressSerializer(serializers.ModelSerializer):
    address = serializers.CharField(required=True)
    house_street_road = serializers.CharField(required=True)
    city = serializers.CharField(required=True)
    user_details = serializers.SerializerMethodField()
    country_details = serializers.SerializerMethodField(read_only=True)
    is_daily_needs = serializers.BooleanField(write_only=True, required=False)
    is_marketplace = serializers.BooleanField(write_only=True, required=False)
    is_services = serializers.BooleanField(write_only=True, required=False)
    is_for_all = serializers.BooleanField(write_only=True, required=False)

    class Meta:
        model = CustomerAddress
        fields = ['id', 'user_details', 'first_name', 'last_name','address', 'house_street_road', 'country', 'country_details', 'city', 'phone_number', 'partner_type', 'is_daily_needs', 'is_marketplace', 'is_services', 'is_for_all']
        read_only_fields = ['id', 'user_details', 'partner_type', 'country']
        #extra_fields = ['address', 'house_street_road', 'city']
        #write_only_fields = ['is_daily_needs', 'is_marketplace', 'is_services', 'is_for_all']

    def get_user_details(self, obj):
        user = User.objects.filter(id=obj.user.id).first()
        serializer = UserSerializerCustom(user, many=False)
        return serializer.data
        
    def get_country_details(self, obj):
        if obj.country:
            serializer  = CustomCountrySerializer(obj.country)
            return serializer.data
        return None
        

class ShippingAddressSerializerCustom(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = ['id', 'title', 'first_name', 'last_name','line1', 'line2', 'postcode', 'country', 'state', 'phone_number', 'notes']
        read_only_fields = ['id']

class BillingAddressSerializerCustom(serializers.ModelSerializer):
    class Meta:
        model = BillingAddress
        fields = ['id', 'title', 'first_name', 'last_name','line1', 'line2', 'postcode', 'country', 'state']
        read_only_fields = ['id']