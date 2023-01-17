import datetime
import pytz
from django.utils.text import slugify
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from oscarapi.serializers.product import (
    ProductImageSerializer,
    ProductStockRecordSerializer,
    AvailabilitySerializer,
    ChildProductSerializer,
    AttributeOptionGroupSerializer,
    ProductAttributeListSerializer,
)
from oscarapi.serializers.checkout import PriceSerializer
from oscarapi.utils.loading import get_api_classes
from oscar.core.loading import get_class

from oscar.apps.search.search_indexes import ProductIndex
from drf_haystack.serializers import HaystackSerializer

from oscar.apps.catalogue.models import (
    ProductClass,
    ProductAttribute,
    ProductAttributeValue,
    ProductImage
)
from oscar.apps.partner.models import StockRecord
from oscarapi.serializers.product import ProductAttributeValueSerializer
from apps.extension.serializers import CustomCategorySerializer
from apps.partner.serializers import ZoneSerializer, PartnerSerializer
from apps.partner.models import Zone, Partner
from .models import Product, Category, Discount, PromoCode
from utils.product_discount import product_discount
from drf_extra_fields.fields import Base64FileField, Base64ImageField
from customapp.serializers import ProductReviewSerializerCustom
from oscar.core.loading import get_model
ProductReview = get_model('reviews', 'ProductReview')

AttributeValueField, CategoryField, SingleValueSlugRelatedField = get_api_classes(
    "serializers.fields",
    ["AttributeValueField", "CategoryField", "SingleValueSlugRelatedField"],
)

Selector = get_class("partner.strategy", "Selector")

class CustomProductAttributeValueSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        read_only=False, queryset=Product.objects.all()
    )
    attribute = serializers.PrimaryKeyRelatedField(
        read_only=False, queryset=ProductAttribute.objects.all()
    )
    # code = serializers.CharField(required=True, write_only=True)
    # value = serializers.CharField(required=True)

    # def create(self, validated_data):
    #     product_id = validated_data.get("product_id", None)
    #     code = validated_data.get("code", None)
    #     value = validated_data.get("value", None)

    #     # check product and code exists
    #     product = get_object_or_404(Product, id=product_id.id, attributes__code=code)
    #     product_attribute_id = product.attributes.get(code=code)

    #     product_attribute_value = get_object_or_404(
    #         ProductAttributeValue,
    #         product_id=product.id,
    #         attribute_id=product_attribute_id.id,
    #     )
    #     product_attribute_value.value = value
    #     product_attribute_value.save()
    #     return product_attribute_value

    class Meta:
        model = ProductAttributeValue
        fields = "__all__"


class CustomProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductClass
        depth = 1
        fields = "__all__"


class CustomProductListSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField(read_only=True)
    price = serializers.SerializerMethodField(read_only=True)
    discount = serializers.SerializerMethodField(read_only=True)
    is_stock = serializers.SerializerMethodField(read_only=True)
    shop = serializers.SerializerMethodField(read_only=True)
    image = serializers.SerializerMethodField(read_only=True)
    is_wishlist = serializers.SerializerMethodField()
    partner_type = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ("id", "title", "image", "category",
                  "slug", "shop", "is_stock", "price",
                  "discount", "rating", "is_wishlist",
                  "partner_type")

    def get_is_wishlist(self, obj):
        request = self.context.get("request")
        user = None
        if request and hasattr(request, "user"):
            user = request.user

        if user:
            if user.is_authenticated:
                if obj.wishlists_lines.filter(wishlist__owner__id=user.id).exists():
                    return True

        return False

    def get_image(self, obj):
        if obj.images:
            return ProductImageSerializer(obj.images.last()).data
        return None
        # return str(obj.primary_image().original)

    def get_shop(self, obj):
        if obj.has_stockrecords:
            partner = obj.stockrecords.first().partner
            data = {
                "id": partner.id,
                "name": partner.name
            }
            return data
        return None

    def get_is_stock(self, obj):
        if obj.has_stockrecords:
            if obj.stockrecords.first().num_in_stock >= 0:
                return True
        return False

    def get_discount(self, obj):
        return product_discount(obj)

    def get_category(self, obj):
        qs = obj.categories.all().last()

        if not qs:
            return None
        data = {
            'id':qs.id,
            'name':qs.name,
            'slug':qs.slug,
        }
        return data

    def get_partner_type(self, obj):
        if obj.categories:
            return obj.categories.first().partner_type.name
        return None

    def get_price(self, obj):
        price = 0
        if obj.structure == "parent":
            qs = Product.objects.filter(parent_id=obj.id)
            if qs:
                if qs.order_by("-stockrecords__price").first().stockrecords.exists():
                    price = (
                        qs.order_by("-stockrecords__price")
                        .first()
                        .stockrecords.first()
                        .price
                    )
            return float(price)
        elif obj.structure == "standalone":
            # price = obj.stockrecords.all().order_by('price').first().price
            if obj.stockrecords.all().order_by("price").exists():
                price = obj.stockrecords.all().order_by("price").first().price
            return float(price)
        elif obj.structure == "child":
            if obj.stockrecords.all().order_by("price").exists():
                price = obj.stockrecords.all().order_by("price").first().price
            return float(price)
        return float(price)

# class CustomProductImageSerializer(serializers.ModelSerializer):
#     original = Base64ImageField()
#     class Meta:
#         model = ProductImage
#         fields = "__all__"
#     def create(self, validated_data):
#         original = validated_data.pop('original', None)
#         if original:
#             return ProductImage.objects.create(original=original, **validated_data)
#         return ProductImage.objects.create(**validated_data)

STRUCTURE = (
    ("parent", "parent"),
    ("standalone", "standalone"),
    ("child", "child"),
)

class CustomProductSerializer(serializers.ModelSerializer):
    structure = serializers.ChoiceField(choices=STRUCTURE)
    images = ProductImageSerializer(many=True, read_only=True)
    price = serializers.SerializerMethodField(read_only=True)
    price_details = serializers.SerializerMethodField(read_only=True)
    discount_detail = serializers.SerializerMethodField(read_only=True)
    # stockrecords = ProductStockRecordSerializer(many=True, read_only=True)
    stockrecord = serializers.SerializerMethodField(read_only=True)
    availability = serializers.SerializerMethodField(read_only=True)
    # children = ChildProductSerializer(many=True, read_only=True)
    # children = CustomProductListSerializer(many=True, read_only=True)
    children = serializers.SerializerMethodField()
    slug = serializers.CharField(read_only=True)
    is_public = serializers.BooleanField(default=False)
    attributes = CustomProductAttributeValueSerializer(
        many=True, read_only=True, source="attribute_values"
    )
    discount = serializers.PrimaryKeyRelatedField(read_only=False, queryset=Discount.objects.all(), required=False)
    parent = serializers.PrimaryKeyRelatedField(
        read_only=False, queryset=Product.objects.all(), required=False
    )
    product_class = serializers.PrimaryKeyRelatedField(
        read_only=False, queryset=ProductClass.objects.all()
    )
    # categories = serializers.PrimaryKeyRelatedField(
    #     many=True, read_only=False, queryset=Category.objects.all()
    # )
    category = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Category.objects.all()
    )
    category = serializers.SerializerMethodField()
    recommended_products = serializers.PrimaryKeyRelatedField(
        many=True, read_only=False, required=False, queryset=Product.objects.all()
    )
    is_wishlist = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()

    class Meta:
        model = Product
        depth = 1
        # fields = "__all__"
        extra_fields = ["images", "stockrecord", "price", "availability", "children", "category"]
        exclude = ("categories",)

    # def to_representation(self, instance):
    #     request = self.context.get("request")
    #     self.fields["product_class"] = CustomProductTypeSerializer(read_only=True, context={"request": request})
    #     self.fields["categories"] = CustomCategorySerializer(read_only=True, many=True, context={"request": request})
    #     self.fields["recommended_products"] = CustomProductSerializer(
    #         read_only=True, many=True, context={"request": request}
    #     )
    #     return super(CustomProductSerializer, self).to_representation(instance)

    def get_category(self, obj):
        category_qs = obj.categories
        category = {}
        if category_qs.exists():
            category_qs = category_qs.first()
            discount = None
            image = None
            thumbnail_image = None
            if category_qs.discount:
                discount = category_qs.discount.id
            if category_qs.image:
                image = category_qs.image
            if category_qs.thumbnail_image:
                thumbnail_image = category_qs.thumbnail_image
            category = {
                "id": category_qs.id,
                "path": category_qs.path,
                "depth": category_qs.depth,
                "numchild": category_qs.numchild,
                "name": category_qs.name,
                "description": category_qs.description,
                "meta_title": category_qs.meta_title,
                "meta_description": category_qs.meta_description,
                # "image": image,
                "slug": category_qs.slug,
                "is_public": category_qs.is_public,
                "ancestors_are_public": category_qs.ancestors_are_public,
                # "thumbnail_image": thumbnail_image,
                "partner_type": category_qs.partner_type.id,
                "discount": discount
            }
            return category
        return None

    def get_stockrecord(self, obj):
        stockrecord_qs = StockRecord.objects.filter(product_id=obj.id)
        stockrecord = {}
        if stockrecord_qs.exists():
            stockrecord_qs = stockrecord_qs.first()
            stockrecord = {
                "id": stockrecord_qs.id,
                "partner_sku": stockrecord_qs.partner_sku,
                "price": stockrecord_qs.price,
                "num_in_stock": stockrecord_qs.num_in_stock,
                "num_allocated": stockrecord_qs.num_allocated,
                "low_stock_threshold": stockrecord_qs.low_stock_threshold,
                "date_created": stockrecord_qs.date_created,
                "date_updated": stockrecord_qs.date_updated,
                "product": stockrecord_qs.product.id,
                "partner": stockrecord_qs.partner.id
            }
            return stockrecord
        return None

    def get_reviews(self, obj):
        product_review_qs = ProductReview.objects.filter(product_id=obj.id)
        serializer = ProductReviewSerializerCustom(instance=product_review_qs, many=True)
        return serializer.data
    
    def get_total_reviews(self, obj):
        product_review_qs = ProductReview.objects.filter(product_id=obj.id)
        return product_review_qs.count()

    def get_children(self, obj):
        request = self.context.get("request")
        return CustomProductSerializer(obj.children.all(), many=True, context={"request": request}).data

    def get_is_wishlist(self, obj):
        request = self.context.get("request")
        user = None
        if request and hasattr(request, "user"):
            user = request.user

        if user:
            if user.is_authenticated:
                if obj.wishlists_lines.filter(wishlist__owner__id=user.id).exists():
                    return True

        return False

    def get_price_details(self, obj):
        request = self.context.get("request")
        user = None
        if request and hasattr(request, "user"):
            user = request.user

        strategy = Selector().strategy(request=request, user=user)
        serializer = PriceSerializer(
            strategy.fetch_for_product(obj).price, context={"request": request}
        )

        return serializer.data

    def get_price(self, obj):
        price = 0
        if obj.structure == "parent":
            qs = Product.objects.filter(parent_id=obj.id)
            if qs:
                if qs.order_by("-stockrecords__price").first().stockrecords.exists():
                    price = (
                        qs.order_by("-stockrecords__price")
                        .first()
                        .stockrecords.first()
                        .price
                    )
            return float(price)
        elif obj.structure == "standalone":
            # price = obj.stockrecords.all().order_by('price').first().price
            if obj.stockrecords.all().order_by("price").exists():
                price = obj.stockrecords.all().order_by("price").first().price
            return float(price)
        elif obj.structure == "child":
            if obj.stockrecords.all().order_by("price").exists():
                price = obj.stockrecords.all().order_by("price").first().price
            return float(price)
        return float(price)

    def get_availability(self, obj):
        request = self.context.get("request")
        user = None
        if request and hasattr(request, "user"):
            user = request.user

        strategy = Selector().strategy(request=request, user=user)
        serializer = AvailabilitySerializer(
            strategy.fetch_for_product(obj).availability, context={"request": request}
        )

        return serializer.data

    def get_discount_detail(self, obj):
        return product_discount(obj)

    def create(self, validated_data):
        title = validated_data.get("title", None)
        structure = validated_data.get("structure")
        product_class = validated_data.pop("product_class", None)
        category = validated_data.pop("category")
        recommended_products = validated_data.pop("recommended_products", None)
        is_discountable = validated_data.get("is_discountable")
        discount = validated_data.get("discount", None)

        if structure == "standalone":
            if validated_data.get("parent"):
                validated_data.pop("parent")

            product_attribute = ProductAttribute.objects.filter(
                product_class_id=product_class
            )

            if is_discountable == False:
                if discount:
                    raise serializers.ValidationError("Can't add discount if discountable is false")

            validated_data["product_class"] = product_class
            product = Product.objects.create(**validated_data)
            product.is_public = False
            product.slug = slugify(title)

            # add category
            if category:
                product.categories.add(category)

            # add recommended product
            if recommended_products:
                for rp in recommended_products:
                    product.recommended_products.add(rp)

            # add product attribute
            if product_attribute.exists():
                for pa in product_attribute:
                    product.attributes.add(pa)

            product.save()
            return product

        if structure == "parent":
            if validated_data.get("parent"):
                validated_data.pop("parent")

            product_attribute = ProductAttribute.objects.filter(
                product_class_id=product_class
            )

            if is_discountable == False:
                if discount:
                    raise serializers.ValidationError("Can't add discount if discountable is false")

            validated_data["product_class"] = product_class
            product = Product.objects.create(**validated_data)
            product.is_public = False
            product.slug = slugify(title)

            # add category
            if category:
                product.categories.add(category)

            # add recommended product
            if recommended_products:
                for rp in recommended_products:
                    product.recommended_products.add(rp)

            # add product attribute
            if product_attribute.exists():
                for pa in product_attribute:
                    product.attributes.add(pa)

            product.save()
            return product

        if structure == "child":
            parent = validated_data.get("parent")
            if not parent:
                raise serializers.ValidationError("Child product must have parent")

            product_attribute = ProductAttribute.objects.filter(
                product_class_id=parent.product_class
            )

            if is_discountable == False:
                if discount:
                    raise serializers.ValidationError("Can't add discount if discountable is false")
            
            product = Product.objects.create(**validated_data)
            product.is_public = False
            product.slug = slugify(title)
            product.product_class = parent.product_class
            product.save()

            # add category
            for category in parent.categories.all():
                product.categories.add(category)

            # add recommanded product
            for rp in parent.recommended_products.all():
                product.recommended_products.add(rp)

            # add product attribute
            if product_attribute.exists():
                for pa in product_attribute:
                    product.attributes.add(pa)

            # product.save()
            return product
    
    def update(self, instance, validated_data):
        category = validated_data.pop("category")
        if instance.categories.exists():
            category_qs = instance.categories
            if category_qs.exists():
                category_rm = category_qs.first()
                instance.categories.remove(category_rm)
        instance.categories.add(category)
        return instance

# class CustomProductVariantSerializer(serializers.ModelSerializer):
#     structure = serializers.CharField(read_only=True, default="child")
#     images = ProductImageSerializer(many=True, read_only=True)
#     price = serializers.SerializerMethodField(read_only=True)
#     price_details = serializers.SerializerMethodField(read_only=True)
#     stockrecords = ProductStockRecordSerializer(many=True, read_only=True)
#     availability = serializers.SerializerMethodField(read_only=True)
#     children = ChildProductSerializer(many=True, read_only=True)
#     slug = serializers.CharField(read_only=True)
#     is_public = serializers.BooleanField(default=False)
#     attributes = ProductAttributeValueSerializer(
#         many=True, read_only=True, source="attribute_values"
#     )
#     product_class = serializers.PrimaryKeyRelatedField(
#         read_only=False, queryset=ProductClass.objects.all(), required=True
#     )
#     categories = serializers.PrimaryKeyRelatedField(
#         many=True, read_only=False, required=True, queryset=Category.objects.all()
#     )
#     recommended_products = serializers.PrimaryKeyRelatedField(
#         many=True, read_only=False, required=False, queryset=Product.objects.all()
#     )
#     # zone = serializers.PrimaryKeyRelatedField(
#     #     read_only=False, required=False, queryset=Zone.objects.all()
#     # )
#     parent = serializers.PrimaryKeyRelatedField(
#         read_only=False, required=True, queryset=Product.objects.all()
#     )

#     class Meta:
#         model = Product
#         depth = 1
#         fields = "__all__"
#         extra_fields = ["images", "stockrecords", "price", "availability", "children"]

#     def to_representation(self, instance):
#         self.fields["product_class"] = CustomProductTypeSerializer(read_only=True)
#         self.fields["categories"] = CustomCategorySerializer(read_only=True, many=True)
#         self.fields["parent"] = CustomProductSerializer(read_only=True)
#         self.fields["recommended_products"] = CustomProductSerializer(
#             read_only=True, many=True
#         )
#         # self.fields["zone"] = ZoneSerializer(read_only=True)
#         return super(CustomProductVariantSerializer, self).to_representation(instance)

#     def get_price_details(self, obj):
#         request = self.context.get("request")
#         user = None
#         if request and hasattr(request, "user"):
#             user = request.user

#         strategy = Selector().strategy(request=request, user=user)
#         serializer = PriceSerializer(
#             strategy.fetch_for_product(obj).price, context={"request": request}
#         )

#         return serializer.data

#     def get_price(self, obj):
#         price = 0
#         if obj.structure == "parent":
#             qs = Product.objects.filter(parent_id=obj.id)
#             if qs.order_by("-stockrecords__price").first().stockrecords.exists():
#                 price = (
#                     qs.order_by("-stockrecords__price")
#                     .first()
#                     .stockrecords.first()
#                     .price
#                 )
#             return float(price)
#         elif obj.structure == "standalone":
#             # price = obj.stockrecords.all().order_by('price').first().price
#             if obj.stockrecords.all().order_by("price").exists():
#                 price = obj.stockrecords.all().order_by("price").first().price
#             return float(price)
#         elif obj.structure == "child":
#             return float(price)
#         return float(price)

#     def get_availability(self, obj):
#         request = self.context.get("request")
#         user = None
#         if request and hasattr(request, "user"):
#             user = request.user

#         strategy = Selector().strategy(request=request, user=user)
#         serializer = AvailabilitySerializer(
#             strategy.fetch_for_product(obj).availability, context={"request": request}
#         )

#         return serializer.data

#     def create(self, validated_data):
#         title = validated_data.get("title", None)
#         product_class = validated_data.get("product_class", None)
#         categories = validated_data.pop("categories")
#         recommended_products = validated_data.get("recommended_products", None)
#         parent = validated_data.get("parent", None)

#         # get parent product
#         parent = get_object_or_404(Product, pk=parent.id)

#         # check if product has stockrecord
#         if parent.has_stockrecords:
#             data = {"data": "", "msg": "Standalone product can't have variant"}
#             return serializers.ValidationError(data)

#         product_attribute = ProductAttribute.objects.filter(
#             product_class_id=product_class
#         )

#         if recommended_products:
#             recommended_products = validated_data.pop("recommended_products")

#         product = Product.objects.create(**validated_data)
#         product.structure = "child"
#         product.is_public = False
#         product.slug = slugify(title)

#         # add category
#         for category in categories:
#             product.categories.add(category)

#         # add recommended product
#         if recommended_products:
#             for rp in recommended_products:
#                 product.recommended_products.add(rp)

#         # add product attribute
#         for pa in product_attribute:
#             product.attributes.add(pa)

#         product.save()
#         return product


class CustomProductAttributeSerializer(serializers.ModelSerializer):
    product_class = serializers.PrimaryKeyRelatedField(
        read_only=False, queryset=ProductClass.objects.all(), required=False
    )
    option_group = AttributeOptionGroupSerializer(required=False, allow_null=True)

    # def to_representation(self, instance):
    #     self.fields["product_class"] = CustomProductTypeSerializer(read_only=True)
    #     return super(CustomProductAttributeSerializer, self).to_representation(instance)

    def create(self, validated_data):
        option_group = validated_data.pop("option_group", None)
        instance = super(CustomProductAttributeSerializer, self).create(validated_data)
        return self.update(instance, {"option_group": option_group})

    def update(self, instance, validated_data):
        option_group = validated_data.pop("option_group", None)
        updated_instance = super(CustomProductAttributeSerializer, self).update(
            instance, validated_data
        )
        if option_group is not None:
            serializer = self.fields["option_group"]
            # use the serializer to update the attribute_values
            if instance.option_group:
                updated_instance.option_group = serializer.update(
                    instance.option_group, option_group
                )
            else:
                updated_instance.option_group = serializer.create(option_group)

            updated_instance.save()

        return updated_instance

    class Meta:
        model = ProductAttribute
        list_serializer_class = ProductAttributeListSerializer
        fields = "__all__"


class ProductSearchSerializer(HaystackSerializer):
    class Meta:
        index_classes = [ProductIndex]
        fields = [
            "text",
            "upc",
            "title",
            "title_exact",
            "product_class",
            "category",
            "price",
            "num_in_stock",
            "rating",
            "suggestions",
            "date_created",
            "date_updated",
        ]



class ProductSearchSerializer(HaystackSerializer):
    class Meta:
        index_classes = [ProductIndex]
        fields = [
            "text",
            "upc",
            "title",
            "title_exact",
            "product_class",
            "category",
            "price",
            "num_in_stock",
            "rating",
            "suggestions",
            "date_created",
            "date_updated",
        ]


class ApproveProductSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(
        many=True, required=True, queryset=Product.objects.all()
    )
    is_public = serializers.BooleanField()

    def create(self, validated_data):
        product = validated_data.get("product", None)
        is_public = validated_data.get("is_public", None)

        for p in product:
            product_qs = Product.objects.get(id=p.id)
            product_qs.is_public = is_public
            product_qs.save()

        return validated_data


class ProductDetailSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    price = serializers.SerializerMethodField(read_only=True)
    # stockrecords = ProductStockRecordSerializer(many=True, read_only=True)
    stockrecords = serializers.SerializerMethodField(read_only=True)
    availability = serializers.SerializerMethodField(read_only=True)
    children = ChildProductSerializer(many=True, read_only=True)
    attributes = ProductAttributeValueSerializer(
        many=True, read_only=True, source="attribute_values"
    )
    product_class = CustomProductTypeSerializer(read_only=True)
    category = serializers.SerializerMethodField(read_only=True)
    recommended_products = serializers.SerializerMethodField(read_only=True)
    zone = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = "__all__"
        # extra_fields = ["images", "stockrecords", "price", "availability", "children"]

    def get_price(self, obj):
        if obj.structure == "parent":
            qs = Product.objects.filter(parent_id=obj.id)
            price = (
                qs.order_by("-stockrecords__price").first().stockrecords.first().price
            )
            return float(price)
        elif obj.structure == "standalone":
            price = obj.stockrecords.all().order_by("price").first().price
            return float(price)
        elif obj.structure == "child":
            return None
        return None

    def get_availability(self, obj):
        request = self.context.get("request")
        user = None
        if request and hasattr(request, "user"):
            user = request.user

        strategy = Selector().strategy(request=request, user=user)
        serializer = AvailabilitySerializer(
            strategy.fetch_for_product(obj).availability, context={"request": request}
        )

        return serializer.data

    def get_category(self, obj):
        if obj.categories:
            serializer = CustomCategorySerializer(obj.categories.last())
            return serializer.data
        return None

    def get_zone(self, obj):
        if obj.zone:
            serializer = ZoneSerializer(obj.zone)
            return serializer.data
        return None

    def get_recommended_products(self, obj):
        if obj.recommended_products:
            serializer = ProductDetailSerializer(obj.recommended_products, many=True)
            return serializer.data
        return None

    def get_stockrecords(self, obj):
        a = "ccccccccccc"
        if obj.stockrecords:
            serializer = ProductStockRecordSerializer(obj.stockrecords, many=True)
            return serializer.data
        return None


class CustomProductStockRecordSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        read_only=False, queryset=Product.objects.all(), required=True
    )
    partner = serializers.PrimaryKeyRelatedField(
        read_only=False, queryset=Partner.objects.all(), required=True
    )
    price = serializers.FloatField(required=True)

    # def to_representation(self, instance):
    #     self.fields["product"] = CustomProductSerializer(read_only=True)
    #     self.fields["partner"] = PartnerSerializer(read_only=True)
    #     return super(CustomProductStockRecordSerializer, self).to_representation(
    #         instance
    #     )

    class Meta:
        model = StockRecord
        fields = "__all__"


class DiscountSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Discount
        fields = "__all__"

    def create(self, validated_data):
        image = validated_data.pop('image', None)
        if image:
            return Discount.objects.create(image=image, **validated_data)
        return Discount.objects.create(**validated_data)


class PromoCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        fields = "__all__"


class CustomPromoCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        fields = "__all__"
        read_only_fields = ["code"]


class DiscountProductSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(
        many=True, required=True, queryset=Product.objects.all()
    )
    discount = serializers.PrimaryKeyRelatedField(
        many=False, required=True, queryset=Discount.objects.all()
    )

    # def create(self, validated_data):
    #     product = validated_data.get("product", None)
    #     discount_qs = validated_data.get("discount", None)

    #     for p in product:
    #         product_qs = Product.objects.get(id=p.id)
    #         product_qs.discount = discount_qs
    #         product_qs.save()

    #     return validated_data

class DiscountCategorySerializer(serializers.Serializer):
    category = serializers.PrimaryKeyRelatedField(many = False, required=True, queryset = Category.objects.all())
    discount = serializers.PrimaryKeyRelatedField(many = False, required=True, queryset = Discount.objects.all())

    # def create(self, validated_data):
    #     category = validated_data.get("category", None)
    #     discount_qs = validated_data.get("discount", None)
    #     product_qs = Product.objects.all(categories=category)

    #     for p in product_qs:
    #         p.discount = discount_qs
    #         p.save()
        
    #     return validated_data

class CustomProductWishlistSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    price = serializers.SerializerMethodField(read_only=True)
    price_details = serializers.SerializerMethodField(read_only=True)
    stockrecords = ProductStockRecordSerializer(many=True, read_only=True)
    availability = serializers.SerializerMethodField(read_only=True)
    children = ChildProductSerializer(many=True, read_only=True)
    slug = serializers.CharField(read_only=True)
    is_public = serializers.BooleanField(default=False)
    attributes = ProductAttributeValueSerializer(
        many=True, read_only=True, source="attribute_values"
    )
    product_class = serializers.PrimaryKeyRelatedField(
        read_only=False, queryset=ProductClass.objects.all(), required=True
    )
    categories = serializers.PrimaryKeyRelatedField(
        many=True, read_only=False, required=True, queryset=Category.objects.all()
    )
    recommended_products = serializers.PrimaryKeyRelatedField(
        many=True, read_only=False, required=False, queryset=Product.objects.all()
    )
    zone = serializers.PrimaryKeyRelatedField(
        read_only=False, required=False, queryset=Zone.objects.all()
    )

    class Meta:
        model = Product
        depth = 1
        fields = "__all__"
        extra_fields = ["images", "stockrecords", "price", "availability", "children"]

    def to_representation(self, instance):
        self.fields["product_class"] = CustomProductTypeSerializer(read_only=True)
        self.fields["categories"] = CustomCategorySerializer(read_only=True, many=True)
        self.fields["recommended_products"] = CustomProductWishlistSerializer(
            read_only=True, many=True
        )
        self.fields["zone"] = ZoneSerializer(read_only=True)
        return super(CustomProductWishlistSerializer, self).to_representation(instance)

    def get_price_details(self, obj):
        request = self.context.get("request")
        user = None
        if request and hasattr(request, "user"):
            user = request.user

        strategy = Selector().strategy(request=request, user=user)
        serializer = PriceSerializer(
            strategy.fetch_for_product(obj.product).price, context={"request": request}
        )

        return serializer.data

    def get_price(self, obj):
        price = 0
        if obj.product.structure == "parent":
            qs = Product.objects.filter(parent_id=obj.id)
            if qs.order_by("-stockrecords__price").first().stockrecords.exists():
                price = (
                    qs.order_by("-stockrecords__price")
                    .first()
                    .stockrecords.first()
                    .price
                )
            return float(price)
        elif obj.product.structure == "standalone":
            # price = obj.stockrecords.all().order_by('price').first().price
            if obj.product.stockrecords.all().order_by("price").exists():
                price = obj.product.stockrecords.all().order_by("price").first().price
            return float(price)
        elif obj.product.structure == "child":
            return float(price)
        return float(price)

    def get_availability(self, obj):
        request = self.context.get("request")
        user = None
        if request and hasattr(request, "user"):
            user = request.user

        strategy = Selector().strategy(request=request, user=user)
        serializer = AvailabilitySerializer(
            strategy.fetch_for_product(obj.product).availability, context={"request": request}
        )

        return serializer.data

    def create(self, validated_data):
        title = validated_data.get("title", None)
        product_class = validated_data.get("product_class", None)
        categories = validated_data.pop("categories")
        recommended_products = validated_data.get("recommended_products", None)

        product_attribute = ProductAttribute.objects.filter(
            product_class_id=product_class
        )

        if recommended_products:
            recommended_products = validated_data.pop("recommended_products")

        product = Product.objects.create(**validated_data)
        product.is_public = False
        product.slug = slugify(title)

        # add category
        for category in categories:
            product.categories.add(category)

        # add recommended product
        if recommended_products:
            for rp in recommended_products:
                product.recommended_products.add(rp)

        # add product attribute
        for pa in product_attribute:
            product.attributes.add(pa)

        product.save()
        return product

class SimpleProductAttributeSerializer(serializers.ModelSerializer):
    product_class = serializers.SerializerMethodField(read_only = True)
    class Meta:
        model = ProductAttribute
        fields = "__all__"
        read_only_fields = ("product_class",'option_group','code')

    def get_product_class(self,obj):
        if obj.product_class:
            return obj.product_class.id
        return None