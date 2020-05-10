from django.contrib import admin

from .models import MenuItem, Topping, SubAddon, Order, OrderItem

# Register your models here.
admin.site.register(MenuItem)
admin.site.register(Topping)
admin.site.register(SubAddon)
admin.site.register(Order)
admin.site.register(OrderItem)
