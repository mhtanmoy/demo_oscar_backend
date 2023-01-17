from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

class ResponseWrapper(Response):

    def __init__(self, data=None, error_code=None, template_name=None, headers=None, exception=False, content_type=None,
                 error_msg=None, msg=None, response_success=True, status=None, data_type=None):
        """
        Alters the init arguments slightly.
        For example, drop 'template_name', and instead use 'data'.

        Setting 'renderer' and 'media_type' will typically be deferred,
        For example being set automatically by the `APIView`.
        """
        status_by_default_for_gz = 200
        if error_code is None and status is not None:
            if status > 299 or status < 200:
                error_code = status
                response_success = False
            else:
                status_by_default_for_gz = status
        if error_code is not None:
            response_success = False


        # output_data = {
        #     "error": {"code": error_code, "error_details": error_msg},
        #     "data": data,
        #     "status": response_success,
        #     "msg": msg if msg else str(error_msg) if error_msg else "Success" if response_success else "Failed",
        # }

        # response parse
        pagination = {
            "count": None,
            "next": None,
            "previous": None
        }
        if data:
            if "results" in data:
                try:
                    if data.get("results") is not None:
                        pagination["count"] = data.pop("count")
                        pagination["next"] = data.pop("next")
                        pagination["previous"] = data.pop("previous")
                        data = data.pop("results")
                    else:
                        error_code = 404
                        error_msg = 'No data found'
                        data = data.pop("results")
                except:
                    pass


        output_data = {
            "error": {"code": error_code, "error_details": error_msg},
            "pagination": pagination,
            "data": data,
            "status": response_success,
            "msg": msg if msg else str(error_msg) if error_msg else "Success" if response_success else "Failed",
        }

        if data_type is not None:
            output_data["type"] = data_type

        # status=200
        super().__init__(data=output_data, status=status,
                         template_name=template_name, headers=headers,
                        exception=exception, content_type=content_type)

class CustomRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context["response"]

        # if response.status_code == 401 or response.status_code == 405 or response.status_code == 403:
        if "error" not in data and response.status_code >= 400 and response.status_code < 500:
            # error
            error_code = response.status_code
            if isinstance(data, list):
                error_msg = str(data)
            else:
                error_msg = data.get("detail")
            response_success = response.status_text
            msg = response.status_text

            # response parse
            pagination = {
                "count": None,
                "next": None,
                "previous": None
            }

            output_data = {
                "error": {"code": error_code, "error_details": error_msg},
                "pagination": pagination,
                "data": None,
                "status": False,
                "msg": msg if msg else str(error_msg) if error_msg else "Success" if response_success else "Failed",
            }
            return super().render(output_data, accepted_media_type, renderer_context)
        return super().render(data, accepted_media_type, renderer_context)