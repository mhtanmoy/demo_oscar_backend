import requests
import datetime
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from decouple import config

from .serializers import (
    TractParcelSerializer,
    LabelPrintSerializer,
    CreateShipmentSerializer,
)
from apps.order.models import Order
from utils.custom_viewset import CustomViewSet
from utils.response_wrapper import ResponseWrapper


class EdeshViewSet(CustomViewSet):
    EDESH_URL = config("EDESH_URL")
    ACCESS_TOKEN = config("EDESH_ACCESS_TOKEN")

    def coverage_area(self, request):
        URL = f"{self.EDESH_URL}/universalapi/allapi/intigratedApi_CoverageArea"
        data = {"accessToken": self.ACCESS_TOKEN}

        try:
            response = requests.post(URL, json=data)
        except:
            return ResponseWrapper(
                error_msg="Something went wrong. Please try again.", error_code=400
            )

        if response.status_code == 200:
            data = response.json()
            del data["status"]
            return ResponseWrapper(data=data, msg="List of all coverage area")
        else:
            return ResponseWrapper(
                error_msg="Something went wrong. Please try again.", error_code=400
            )

    def tract_parcel(self, request):
        serializer = TractParcelSerializer(data=request.data)
        if serializer.is_valid():
            access_id = serializer.validated_data.get("access_id")
            product_waybill = serializer.validated_data.get("product_waybill")

            URL = f"{self.EDESH_URL}/universalapi/allapi/unAuthorized_parcel_tracking?company_name=EDESH"
            data = {
                "accessToken": self.ACCESS_TOKEN,
                "access_id": access_id,
                "product_waybill": product_waybill,
            }

            try:
                response = requests.post(URL, json=data)
            except:
                return ResponseWrapper(
                    error_msg="Something went wrong. Please try again.", error_code=400
                )

            if response.status_code == 200:
                data = response.json()
                del data["status"]
                return ResponseWrapper(data=data, msg="Tract Parcel")
            else:
                return ResponseWrapper(
                    error_msg="Something went wrong. Please try again.", error_code=400
                )
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400)

    def label_print(self, request):
        serializer = LabelPrintSerializer(data=request.data)
        if serializer.is_valid():
            reference_list = serializer.validated_data.get("reference_list")
            start_date = serializer.validated_data.get("start_date")
            finish_date = serializer.validated_data.get("finish_date")

            URL = f"{self.EDESH_URL}/universalapi/allapi/intigratedApi_LabelPrinting"
            data = {
                "accessToken": self.ACCESS_TOKEN,
                "startDate": start_date.isoformat(),
                "finishDate": finish_date.isoformat(),
            }

            if reference_list:
                data["referenceList"] = reference_list
            else:
                data["referenceList"] = []

            try:
                response = requests.post(URL, json=data)
            except:
                return ResponseWrapper(
                    error_msg="Something went wrong. Please try again.", error_code=400
                )

            if response.status_code == 200:
                data = response.json()
                del data["status"]
                return ResponseWrapper(data=data, msg="Label Print")
            else:
                return ResponseWrapper(
                    error_msg="Something went wrong. Please try again.", error_code=400
                )
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400)

    def create_shipment(self, request):
        URL = (
            f"{self.EDESH_URL}/universalapi/allapi/intigratedApi_ClientShipment_Upload"
        )
        dt = datetime.datetime.now().isoformat()
        serializer = CreateShipmentSerializer(data=request.data)

        if serializer.is_valid():
            reference_no = serializer.validated_data.get("reference_no")

            # check valid order
            payload = []
            for reference in reference_no:
                order = get_object_or_404(Order, number__exact=reference)
                order_payload = {
                    "REFERENCE_NO": order.number,
                    "CONSIGNEE_NAME": order.user.username,
                    "ADDRESS": order.shipping_address.line1,
                    "DISTRICT_CITY": order.shipping_address.state,
                    "COVERAGE_AREA": "coverage_area",
                    "CONTACT_NUMBER": order.user.phone,
                    "EMERGENCY_NUMBER": "emergency_number",
                    "WEIGHT": "weight",
                    "PAYMENT_TYPE": order.shipping_method,
                    "ACTUAL_PRICE": order.total_incl_tax,
                    "COD_AMOUNT": order.total_incl_tax + order.shipping_incl_tax,
                    "PRODUCT_TO_BE_SHIFT": "solid",
                    "isNextdayShipment": 0,
                    "isOpenBoxShipment": 1,
                }
                payload.append(order_payload)

            data = {
                "accessToken": self.ACCESS_TOKEN,
                "dateTime": dt,
                "payload": payload,
            }

            print(data)

            # try:
            #     response = requests.post(URL, json=data)
            # except:
            #     return ResponseWrapper(
            #         error_msg="Something went wrong. Please try again.", error_code=400
            #     )

            # if response.status_code == 200:
            #     data = response.json()
            #     del data["status"]
            #    return ResponseWrapper(data="data", msg="Create Shipment Successful")
            # else:
            #     return ResponseWrapper(
            #         error_msg="Something went wrong. Please try again.", error_code=400
            #     )

            return ResponseWrapper(data=data, msg="Create Shipment Successful")
        else:
            return ResponseWrapper(error_msg=serializer.errors, error_code=400)
