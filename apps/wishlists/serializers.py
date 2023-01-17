from oscar.apps.wishlists.models import *  # noqa isort:skip
from rest_framework import serializers

from oscar.apps.wishlists.models import Line
# from apps.catalogue.serializers import CustomProductSerializer
# from apps.catalogue.models import Product

class LineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Line
        depth = 2
        exclude = ('wishlist',)

    # def to_representation(self, instance):
    #     instance = super(LineSerializer, self).to_representation(instance)
    #     product = Product.objects.filter(id=instance['product']['id']).first()
    #     serializer = CustomProductSerializer(instance=product, many=False)

    #     instance['product'] = serializer.data
    #     return super(LineSerializer, self).to_representation(instance)


class WishlistSerializer(serializers.ModelSerializer):
    product_list = serializers.SerializerMethodField()

    class Meta:
        model = WishList
        depth = 1
        fields = "__all__"
    
    def get_product_list(self, obj):
        products = obj.lines.all()
        serializer = LineSerializer(products, many=True)
        return serializer.data

class WishlistCreateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()

