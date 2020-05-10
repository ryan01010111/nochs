from django.db import models
from django.contrib.auth.models import User

SIZES = [
    ('S', 'Small'),
    ('L', 'Large'),
    (None, 'N/A')
]

# Create your models here.
class MenuItem(models.Model):

    category = models.CharField(max_length=64)
    style = models.CharField(max_length=64)
    toppings_qty = models.IntegerField()
    price_small = models.DecimalField(max_digits=8, null=True, decimal_places=2, default=0.00)
    price_large = models.DecimalField(max_digits=8, null=True, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.category}, {self.style}"


class Topping(models.Model):

    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class SubAddon(models.Model):

    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Order(models.Model):

    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="orders")
    total_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    complete = models.BooleanField(default=False)
    timestamp = models.DateTimeField()

    def calc_total_cost(self):

        order_items = self.orderItems.all()
        total = 0.00
        for item in order_items:
            total += float(item.price)
        
        return total

    def format_timestamp(self):

        return self.timestamp.strftime("%m/%d %H:%M:%S")

    def __str__(self):
        return f"{self.user.last_name}, {self.user.first_name}, {self.total_cost}, {self.complete}"


class OrderItem(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="orderItems")
    menu_item = models.ForeignKey(MenuItem, null=True, on_delete=models.SET_NULL)
    toppings = models.ManyToManyField(Topping, related_name="orderToppings")
    sub_addons = models.ManyToManyField(SubAddon, related_name="orderAddons")
    size = models.CharField(max_length=1, choices=SIZES, default=None)
    qty = models.IntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    def calc_price(self):

        if self.size == "S":
            item_price = float(self.menu_item.price_small)
        else:
            item_price = float(self.menu_item.price_large)

        sub_addons = self.sub_addons.all()
        if sub_addons:
            item_price += (len(sub_addons) * 0.50)

        return item_price * self.qty

    def __str__(self):

        addons = ""

        toppings = self.toppings.all()
        if toppings:
            for topping in toppings:
                addons += f", {topping}"

        sub_addons = self.sub_addons.all()
        if sub_addons:
            for addon in sub_addons:
                addons += f", {addon}"

        return f"order number({self.order.pk}), menu item({self.menu_item.category}, {self.menu_item.style}{addons}), size({self.size}), qty({self.qty}), price({self.price})"
