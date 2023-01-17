import datetime, pytz

def product_discount(obj):
    current_datetime = datetime.datetime.now(pytz.timezone("Asia/Dhaka"))
    current_date = current_datetime.date()
    current_time = current_datetime.time()
    price = 0
    try:
        if obj.stockrecords.all().order_by("price").exists():
            price = float(obj.stockrecords.all().order_by("price").first().price)
    except:
        pass
    valid = {}

    if obj.discount:
        discount_type = obj.discount.discount_type
        schedule_type = obj.discount.schedule_type
        amount = obj.discount.amount

        if schedule_type == "Time_Wise":
            start_time = obj.discount.start_time
            end_time = obj.discount.end_time

            if discount_type == "PERCENTAGE":
                if end_time >= current_time >= start_time:
                    valid["id"] = obj.discount.id
                    valid["title"] = obj.discount.title
                    if price != 0:
                        dp = price - (price * (amount / 100))
                        valid["price"] = dp

            if discount_type == "AMOUNT":
                if end_time >= current_time >= start_time:
                    valid["id"] = obj.discount.id
                    valid["title"] = obj.discount.title
                    if price != 0:
                        dp = price - amount
                        valid["price"] = dp

        if schedule_type == "Date_Wise":
            start_date = obj.discount.start_date
            end_date = obj.discount.end_date

            if discount_type == "PERCENTAGE":
                if end_date >= current_date >= start_date:
                    valid["id"] = obj.discount.id
                    valid["title"] = obj.discount.title
                    if price != 0:
                        dp = price - (price * (amount / 100))
                        valid["price"] = dp

            if discount_type == "AMOUNT":
                if end_date >= current_date >= start_date:
                    valid["id"] = obj.discount.id
                    valid["title"] = obj.discount.title
                    if price != 0:
                        dp = price - amount
                        valid["price"] = dp

    return valid if valid else None