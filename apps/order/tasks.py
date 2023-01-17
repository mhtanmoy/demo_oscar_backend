from celery import shared_task
from django.core.mail import send_mail
from amarshohor_backend.settings import EMAIL_HOST_USER


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 7, "countdown": 5},
)
def send_mail_service(self, subject, message, receivers):
    if (
        len(subject.strip()) == 0
        and len(message.strip()) == 0
        and len(receivers.strip()) == 0
    ):
        raise Exception()
    send_mail(
        subject=subject,
        message=message,
        from_email=EMAIL_HOST_USER,
        recipient_list=[receivers],
        fail_silently=False,
    )
    return "Mail Successfully Sent"


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 7, "countdown": 5},
)
def send_order_pending_notification(self, order_number):
    if len(order_number.strip()) == 0:
        raise Exception()
    print(f"Order {order_number} pending")
    return f"Order {order_number} pending notification sent"


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 7, "countdown": 5},
)
def send_order_confirm_notification(self, order_number):
    if len(order_number.strip()) == 0:
        raise Exception()
    print(f"Order {order_number} confirm")
    return f"Order {order_number} confirm notification sent"


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 7, "countdown": 5},
)
def send_order_picked_notification(self, order_number):
    if len(order_number.strip()) == 0:
        raise Exception()
    print(f"Order {order_number} picked successfully")
    return f"Order {order_number} picked notification sent"


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 7, "countdown": 5},
)
def send_order_delivered_notification(self, order_number):
    if len(order_number.strip()) == 0:
        raise Exception()
    print(f"Order {order_number} has been delivered")
    return f"Order {order_number} delivered notification sent"


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 7, "countdown": 5},
)
def send_order_return_notification(self, order_number):
    if len(order_number.strip()) == 0:
        raise Exception()
    print(f"Order {order_number} has been returned")
    return f"Order {order_number} returned notification sent"


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 7, "countdown": 5},
)
def send_order_cancel_notification(self, order_number):
    if len(order_number.strip()) == 0:
        raise Exception()
    print(f"Order {order_number} has been canceled")
    return f"Order {order_number} cencal notification sent"


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 7, "countdown": 5},
)
def send_order_item_cancel_notification(self, order_item_name):
    if len(order_item_name.strip()) == 0:
        raise Exception()
    print(f"Order item {order_item_name} has been canceled")
    return f"Order item {order_item_name} cencal notification sent"


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 7, "countdown": 5},
)
def send_order_unavailable_notification(self, order_item_name):
    if len(order_item_name.strip()) == 0:
        raise Exception()
    print(f"Order {order_item_name} unavailable")
    return f"Order {order_item_name} unavailable notification sent"
