from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("menu", views.menu_view, name="menu"),
    path("add_order_item", views.add_order_item, name="add_order_item"),
    path("cart", views.cart_view, name="cart"),
    path("order_remove_item/<int:item_num>/", views.order_remove_item, name="order_remove_item"),
    path("order_payment/<int:order_num>/", views.order_payment, name="order_payment"),
    path("create_payment", views.create_payment, name="create_payment"),
    path("complete_order", views.complete_order, name="complete_order"),
    path("order_tracker", views.order_tracker, name="order_tracker")
]
