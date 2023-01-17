from rest_framework import serializers
from .models import Zone, SubZone, Partner, PartnerType
from apps.order.models import OrderCountPerSchedule
from apps.order.serializers import ScheduleSerializer
from drf_extra_fields.fields import Base64FileField, Base64ImageField

class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = "__all__"


class SubZoneSerializer(serializers.ModelSerializer):
    zone = serializers.PrimaryKeyRelatedField(queryset=Zone.objects.all())

    # def to_representation(self, instance):
    #     self.fields["zone"] = ZoneSerializer(read_only=True)
    #     return super(SubZoneSerializer, self).to_representation(instance)

    class Meta:
        model = SubZone
        fields = "__all__"

class PartnerSerializer(serializers.ModelSerializer):
    logo = Base64ImageField()
    users = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    class Meta:
        model = Partner
        fields = "__all__"
        read_only_fields = ['code']

    def create(self, validated_data):
        logo = validated_data.pop('logo', None)
        if logo:
            return Partner.objects.create(logo=logo, **validated_data)
        return Partner.objects.create(**validated_data)



class PartnerTypeSerializer(serializers.ModelSerializer):
    slug = serializers.CharField(read_only=True)
    class Meta:
        model = PartnerType
        fields = "__all__"
