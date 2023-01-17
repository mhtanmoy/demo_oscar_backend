from rest_framework import serializers
from django.contrib.auth import get_user_model
from oscar.core.loading import get_model

Order = get_model('order', 'Order')
User = get_user_model()

class Customer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email")


class OrderHistorySerializer(serializers.ModelSerializer):
    user = Customer()

    class Meta:
        model = Order
        depth = 1
        fields = "__all__"