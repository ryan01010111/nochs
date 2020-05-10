from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse
from django.db.models import Count
from django.utils import timezone
import os
import json
import stripe

from .models import MenuItem, Topping, SubAddon, Order, OrderItem
from .helpers import get_cart_count

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Create your views here.
def index(request):

    user = request.user

    if not user.is_authenticated:
        return render(request, "orders/login.html", {"message": None})

    context = {
        "user": user,
        "cart_item_count": get_cart_count(user)
    }
    return render(request, "orders/index.html", context)


def login_view(request):

    if request.method == "POST":

        try:
            username = request.POST["username"]
        except KeyError:
            return render(request, "orders/login.html", {"message": "Please provide your username"})

        try:
            password = request.POST["password"]
        except KeyError:
            return render(request, "orders/login.html", {"message": "Please provide your password"})

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))

        else:
            return render(request, "orders/login.html", {"message": "Invalid username and/or password"})

    else:
        return HttpResponseRedirect(reverse("index"))


def logout_view(request):

    logout(request)
    return render(request, "orders/login.html", {"message": "You have been logged out"})


def register(request):

    if request.method == "POST":

        firstName = request.POST["firstName"]
        if not firstName:
            return render(request, "orders/register.html", {"message": "Please provide your first name"})
        lastName = request.POST["lastName"]
        if not lastName:
            return render(request, "orders/register.html", {"message": "Please provide your last name"})
        email = request.POST["email"]
        if not email:
            return render(request, "orders/register.html", {"message": "Please provide your email address"})
        username = request.POST["username"]
        if not username:
            return render(request, "orders/register.html", {"message": "Please enter a username"})
        password = request.POST["password"]
        if not password:
            return render(request, "orders/register.html", {"message": "Please enter a password"})
        passwordConfirmation = request.POST["passwordConfirmation"]
        if not passwordConfirmation:
            return render(request, "orders/register.html", {"message": "Please confirm your password"})
        if password != passwordConfirmation:
            return render(request, "orders/register.html", {"message": "Those passwords don't match"})

        # create user
        User.objects.create_user(username=username, password=password, email=email, first_name=firstName, last_name=lastName)

        # log user in
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))

    else:

        return render(request, "orders/register.html")
    

@login_required()
def menu_view(request):

    user = request.user

    context = {
        "cart_item_count": get_cart_count(user),
        "regular_pizzas": MenuItem.objects.filter(category="Regular Pizza"),
        "sicilian_pizzas": MenuItem.objects.filter(category="Sicilian Pizza"),
        "subs": MenuItem.objects.filter(category="Sub"),
        "pastas": MenuItem.objects.filter(category="Pasta"),
        "salads": MenuItem.objects.filter(category="Salad"),
        "dinner_platters": MenuItem.objects.filter(category="Dinner Platter"),
        "toppings": Topping.objects.all(),
        "sub_extras": SubAddon.objects.all()
    }

    return render(request, "orders/menu.html", context)


@login_required()
def add_order_item(request):

    if request.method == "POST":

        # JSON error response template
        errResponse = JsonResponse({"success": False})

        data = json.loads(request.POST["itemData"])

        user = request.user

        # fetch existing order or create new one
        try:
            order = user.orders.get(complete=False)
        except Order.DoesNotExist:
            order = Order(user=user, timestamp=timezone.now())
            order.save()

        # fetch requested menu item
        try:
            menu_item = MenuItem.objects.get(pk=data["itemId"])
        except MenuItem.DoesNotExist:
            return errResponse

        if data["size"] not in ["S", "L"] or int(data["qty"]) > 100:
            return errResponse

        # fetch requested toppings
        toppings = []
        if data["toppings"]:
            for key in data["toppings"]:
                try:
                    tp = Topping.objects.get(pk=key)
                    toppings.append(tp)
                except Topping.DoesNotExist:
                    return errResponse

        # ensure max topping qty met and not exceeded
        if len(data["toppings"]) != menu_item.toppings_qty:
            return errResponse

        # fetch requested sub addons
        sub_addons = []
        if data["sub_extras"]:
            for key in data["sub_extras"]:
                try:
                    sa = SubAddon.objects.get(pk=key)
                    sub_addons.append(sa)
                except SubAddon.DoesNotExist:
                    return errResponse

        order_item = OrderItem(order=order, menu_item=menu_item, size=data["size"], qty=int(data["qty"]))
        order_item.save()

        if toppings:
            for tp in toppings:
                order_item.toppings.add(tp)
        if sub_addons:
            for sa in sub_addons:
                order_item.sub_addons.add(sa)

        order_item.price = order_item.calc_price()
        order_item.save()

        order.total_cost = order.calc_total_cost()
        order.save()

        orderItemCount = order.orderItems.all().count()

        return JsonResponse({

            "success": True,
            "itemCount": orderItemCount
        })


@login_required()
def cart_view(request):

    user = request.user

    try:
        order = user.orders.get(complete=False)
    except Order.DoesNotExist:
        order = None

    if order and order.orderItems.all().count() > 0:

        order.total_cost = order.calc_total_cost()
        order.save()
        
        context = {
            "order": order,
            "order_items": order.orderItems.all(),
            "cart_item_count": order.orderItems.all().count()
        }

    else:
        context = None

    return render(request, "orders/cart.html", context)


@login_required()
def order_remove_item(request, item_num):

    try:
        order_item = OrderItem.objects.get(pk=item_num)
    except OrderItem.DoesNotExist:
        return HttpResponse(status=403)

    order = order_item.order
    if order.user != request.user:
        return HttpResponse(status=403)        

    order_item.delete()

    return HttpResponseRedirect(reverse("cart"))


@login_required()
def order_payment(request, order_num):

    user = request.user

    try:
        order = Order.objects.get(pk=order_num)
    except Order.DoesNotExist:
        return HttpResponseRedirect(reverse("index"))

    context = {
        "cart_item_count": get_cart_count(user),
        "order_num": order_num,
        "order_total": order.calc_total_cost()
    }

    return render(request, "orders/order_payment.html", context)


@login_required()        
def create_payment(request):

    if request.method == "POST":

        try:
            data = json.loads(request.body)

            try:
                order = Order.objects.get(pk=data["order"])
            except Order.DoesNotExist:
                return JsonResponse({"error": "Order does not exist"}, status=403)

            if order.user != request.user:
                return JsonResponse({"error": "Order number does not match user"}, status=403)

            total_cost = order.calc_total_cost()
            order.total_cost = total_cost
            order.timestamp = timezone.now()
            order.save()

            intent = stripe.PaymentIntent.create(
                amount=int(total_cost * 100),   #Stripe takes amount in smallest unit of currency (pennies)
                currency="usd"
            )
            return JsonResponse({
            "clientSecret": intent["client_secret"]
            })
            
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=403)


@login_required()
def complete_order(request):

    if request.method == "POST":

        data = json.loads(request.body)

        try:
            order = Order.objects.get(pk=data["order"])
        except Order.DoesNotExist:
            return HttpResponse(status=403)

        if order.user != request.user:
            return HttpResponse(status=403)

        order.complete = True
        order.save()

        return HttpResponse(status=200)


@login_required()
@permission_required("orders.view_order")
def order_tracker(request):

    context = {
        "orders": Order.objects.filter(complete=True).order_by("-timestamp")
    }

    return render(request, "orders/order_tracker.html", context)
