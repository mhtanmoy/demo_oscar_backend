from oscar.apps.order.admin import *  # noqa
from .models import *
from oscar.apps.basket.models import Basket

admin.site.register(OrderReturn)
admin.site.register(Schedule)
admin.site.register(OrderCountPerSchedule)
# admin.site.register(Basket)