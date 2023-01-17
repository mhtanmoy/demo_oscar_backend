from rest_framework.exceptions import NotFound,ErrorDetail, APIException
from rest_framework.utils.serializer_helpers import ReturnDict, ReturnList
from rest_framework import status
from django.utils.translation import gettext_lazy as _

class NotFoundExtended(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _('A server error occurred.')
    default_code = 'error'

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = str(self.default_detail)
        if code is None:
            code = str(self.default_code)

        self.detail = detail

#     def __str__(self):
#         return self.detail

#     def _get_error_details(self,data, default_code=None):
#         """
#         Descend into a nested data structure, forcing any
#         lazy translation strings or strings into `ErrorDetail`.
#         """
#         # if isinstance(data, (list, tuple)):
#         #     ret = [
#         #         self._get_error_details(item, default_code) for item in data
#         #     ]
#         #     if isinstance(data, ReturnList):
#         #         return ReturnList(ret, serializer=data.serializer)
#         #     return ret
#         # elif isinstance(data, dict):
#         #     ret = {
#         #         key: self._get_error_details(value, default_code)
#         #         for key, value in data.items()
#         #     }
#         #     if isinstance(data, ReturnDict):
#         #         return ReturnDict(ret, serializer=data.serializer)
#         #     return ret

#         # # text = data
#         # code = getattr(data, 'code', default_code)
#         # return ErrorDetail(data, default_code)
#         return data
   


#     def get_codes(self):
#         """
#         Return only the code part of the error details.

#         Eg. {"name": ["required"]}
#         """
#         return _get_codes(self.detail)

#     def get_full_details(self):
#         """
#         Return both the message & code parts of the error details.

#         Eg. {"name": [{"message": "This field is required.", "code": "required"}]}
#         """
#         return _get_full_details(self.detail)

# def _get_codes(detail):
#     if isinstance(detail, list):
#         return [_get_codes(item) for item in detail]
#     elif isinstance(detail, dict):
#         return {key: _get_codes(value) for key, value in detail.items()}
#     return detail.code


# def _get_full_details(detail):
#     if isinstance(detail, list):
#         return [_get_full_details(item) for item in detail]
#     elif isinstance(detail, dict):
#         return {key: _get_full_details(value) for key, value in detail.items()}
#     return {
#         'message': detail,
#         'code': detail.code
#     }