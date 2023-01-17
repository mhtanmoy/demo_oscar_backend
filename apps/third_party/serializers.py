from rest_framework import serializers


class TractParcelSerializer(serializers.Serializer):
    access_id = serializers.IntegerField()
    product_waybill = serializers.CharField()


class LabelPrintSerializer(serializers.Serializer):
    reference_list = serializers.ListField(
        child=serializers.CharField(required=False), required=False
    )
    start_date = serializers.DateTimeField()
    finish_date = serializers.DateTimeField()


class CreateShipmentSerializer(serializers.Serializer):
    reference_no = serializers.ListField(child=serializers.CharField())
