
from django.contrib.auth.models import User
from .models import Order

def get_cart_count(user):

    try:
        existingOrder = user.orders.get(complete=False)
    except Order.DoesNotExist:
        return None

    return existingOrder.orderItems.all().count()