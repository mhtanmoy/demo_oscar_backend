# custom pagination
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from collections import OrderedDict
from django.core.paginator import InvalidPage
from rest_framework.exceptions import NotFound
from utils.NotFoundExtended import NotFoundExtended
from rest_framework.renderers import JSONRenderer
import json
from rest_framework.pagination import LimitOffsetPagination


class CustomPagination(PageNumberPagination):
    page_size = 10000000000000
    page_size_query_param = 'page_size'
    max_page_size = 10000000000000000

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = self.get_page_number(request, paginator)

        try:
            self.page = paginator.page(page_number)
        except InvalidPage as exc:
            # msg = self.invalid_page_message.format(
            #     page_number=page_number, message=str(exc)
            # )
            output_data = {
                "error": {"code": 404, "error_details": 'Invalid page.'},
                "pagination": {
                    "count": None,
                    "next": None,
                    "previous": None
                },
                "data": None,
                "status": False,
                "msg": 'Failed',
            }

            # raise NotFound(msg)
            # raise NotFound(output_data)
            raise NotFoundExtended(output_data)
            # return JSONRenderer.render()
            # return None

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)



class CustomLimitPagination(LimitOffsetPagination):
    default_limit = 10
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 100

    """


    page = self.paginate_queryset(booking_list_qs)
    serializer = self.get_serializer(page, many=True)
    paginated_data = self.get_paginated_response(serializer.data)
    """


class NoLimitPagination(LimitOffsetPagination):
    # default_limit = 1000000000
    # limit_query_param = 'limit'
    # offset_query_param = 'offset'
    # max_limit = 1000000000
    def paginate_queryset(self, queryset, request, view=None):
        self.count = self.get_count(queryset)
        self.limit = self.get_limit(request)
        self.offset = self.get_offset(request)
        self.request = request
        self.display_page_controls = False
