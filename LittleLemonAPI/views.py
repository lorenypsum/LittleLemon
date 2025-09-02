from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from django.contrib.auth.models import User, Group
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import AnonRateThrottle
from .models import Category, MenuItem, Rating, Cart, Order, OrderItem
from .serializers import (
    MenuItemSerializer,
    RatingSerializer,
    ManagerSerializer,
    DeliveryCrewSerializer,
    CartSerializer,
    OrderSerializer,
    OrderItemSerializer,
    CategorySerializer,
)
from .throttles import TenCallsPerMinute


# Create your views here.
@api_view(["GET", "POST", "PUT", "DELETE", "PATCH"])
@permission_classes([IsAuthenticated])
def menu_items(request):
    if request.method == "GET":
        items = MenuItem.objects.select_related("category").all()
        category_name = request.query_params.get("category")
        to_price = request.query_params.get("to_price")
        search = request.query_params.get("search")
        ordering = request.query_params.get("ordering")
        perpage = request.query_params.get("perpage", default=2)
        page = request.query_params.get("page", default=1)

        if category_name:
            items = items.filter(category__title=category_name)
        if to_price:
            items = items.filter(price__lte=to_price)
        if search:
            items = items.filter(title__contains=search)
        if ordering:
            ordering_fields = ordering.split(",")
            items = items.order_by(*ordering_fields)

        paginator = Paginator(items, per_page=perpage)
        try:
            items = paginator.page(number=page)
        except EmptyPage:
            items = []
        serialized_item = MenuItemSerializer(items, many=True)
        return Response(serialized_item.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        if not request.user.groups.filter(name="Manager").exists():
            return Response(
                {"message": "You are not authorized to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serialized_item = MenuItemSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()
        return Response(serialized_item.data, status=status.HTTP_201_CREATED)

    if request.method in ["PUT", "PATCH", "POST", "DELETE"]:
        if not request.user.groups.filter(name="Manager").exists():
            return Response(
                {"message": "You are not authorized to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )


@api_view(["GET", "POST", "PUT", "DELETE", "PATCH"])
def single_item(request, id):
    if request.methor == "GET":
        item = get_object_or_404(MenuItem, id=id)
        serialized_item = MenuItemSerializer(item)
        return Response(serialized_item.data, status=status.HTTP_200_OK)
    if request.method in ["PUT", "PATCH"]:
        if request.user.groups.filter(name="Manager").exists() is False:
            return Response(
                {"message": "You are not authorized to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )
        else:
            item = get_object_or_404(MenuItem, id=id)
            serialized_item = MenuItemSerializer(item, data=request.data)
            serialized_item.is_valid(raise_exception=True)
            serialized_item.save()
            return Response(serialized_item.data, status=status.HTTP_200_OK)
    if request.method == "DELETE":
        if request.user.groups.filter(name="Manager").exists() is False:
            return Response(
                {"message": "You are not authorized to perform this action."},
                status=status.HTTP_403_FORBIDDEN,
            )
        else:
            item = get_object_or_404(MenuItem, id=id)
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def managers(request):
    if request.method == "GET":
        managers = User.objects.filter(groups__name="Manager")
        serialized_managers = ManagerSerializer(managers, many=True)
        return Response(serialized_managers.data, status=status.HTTP_200_OK)
    if request.method == "POST":
        username = request.data.get("username")
        if username:
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name="Manager")
            managers.user_set.add(user)
            return Response({"message": "Created."}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"error": "Username not provided."}, status=status.HTTP_400_BAD_REQUEST
            )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def single_manager(request, id):
    manager = get_object_or_404(User, id=id)
    if request.method == "DELETE":
        if manager.groups.filter(name="Manager").exists():
            managers = Group.objects.get(name="Manager")
            managers.user_set.remove(manager)
            return Response({"message": "Deleted."}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "User is not a manager."}, status=status.HTTP_400_BAD_REQUEST
            )


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def delivery_crew(request):
    if request.method == "GET":
        delivery_crew = User.objects.filter(groups__name="Delivery")
        serialized_delivery_crew = DeliveryCrewSerializer(delivery_crew, many=True)
        return Response(serialized_delivery_crew.data, status=status.HTTP_200_OK)
    if request.method == "POST":
        username = request.data.get("username")
        if username:
            user = get_object_or_404(User, username=username)
            delivery_crew = Group.objects.get(name="Delivery")
            delivery_crew.user_set.add(user)
            return Response({"message": "Created."}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"error": "Username not provided."}, status=status.HTTP_400_BAD_REQUEST
            )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def single_delivery_crew(request, id):
    delivery_crew = get_object_or_404(User, id=id)
    if request.method == "DELETE":
        if delivery_crew.groups.filter(name="Delivery").exists():
            delivery_crew_group = Group.objects.get(name="Delivery")
            delivery_crew_group.user_set.remove(delivery_crew)
            return Response({"message": "Deleted."}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "User is not a delivery crew member."},
                status=status.HTTP_400_BAD_REQUEST,
            )

@api_view()
@throttle_classes([AnonRateThrottle])
def throttle_check(request):
    return Response({"message": "This is a throttled view!"})


@api_view()
@permission_classes([IsAuthenticated])
@throttle_classes([TenCallsPerMinute])
def throttle_check_auth(request):
    return Response(
        {"message": "This is a throttled view for authenticated users!"},
        status=status.HTTP_429_TOO_MANY_REQUESTS,
    )


@api_view(["GET", "POST", "DELETE"])
@permission_classes([IsAuthenticated])
def cart(request):
    if request.method == "GET":
        carts = Cart.objects.filter(user=request.user)
        serialized_carts = CartSerializer(carts, many=True)
        return Response(serialized_carts.data, status=status.HTTP_200_OK)
    if request.method == "POST":
        data = request.data.copy()
        data["user"] = request.user.id
        menuitem_id = data.get("menuitem")
        quantity = data.get("quantity", 1)
        if not menuitem_id:
            return Response(
                {"error": "Menu item ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            menuitem = MenuItem.objects.get(id=menuitem_id)
        except MenuItem.DoesNotExist:
            return Response(
                {"error": "Menu item not found."}, status=status.HTTP_404_NOT_FOUND
            )
        if menuitem.inventory < int(quantity):
            return Response(
                {"error": "Insufficient inventory."}, status=status.HTTP_400_BAD_REQUEST
            )
        unit_price = menuitem.price
        price = unit_price * int(quantity)
        data["unit_price"] = unit_price
        data["price"] = price
        serialized_cart = CartSerializer(data=data)
        serialized_cart.is_valid(raise_exception=True)
        serialized_cart.save()
        menuitem.inventory -= int(quantity)
        menuitem.save()
        return Response(serialized_cart.data, status=status.HTTP_201_CREATED)
    if request.method == "DELETE":
        carts = Cart.objects.filter(user=request.user, order_placed=False)
        if not carts.exists():
            return Response(
                {"error": "No items in cart to delete."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        for cart in carts:
            menuitem = cart.menuitem
            menuitem.inventory += cart.quantity
            menuitem.save()
            cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def orders(request):
    if request.method == "GET":
        if request.user.groups.filter(name="Manager").exists():
            orders = Order.objects.all()
        else:
            orders = Order.objects.filter(user=request.user)
        serialized_orders = OrderSerializer(orders, many=True)
        return Response(serialized_orders.data, status=status.HTTP_200_OK)
    if request.method == "POST":
        carts = Cart.objects.filter(user=request.user)
        if not carts.exists():
            return Response(
                {"error": "No items in cart to place an order."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        total = sum(cart.price for cart in carts)
        order = Order.objects.create(user=request.user, total=total)
        for cart in carts:
            OrderItem.objects.create(
                order=order,
                menuitem=cart.menuitem,
                quantity=cart.quantity,
                unit_price=cart.unit_price,
                price=cart.price,
            )
            cart.order_placed = True
            cart.save()
        carts.delete()
        serialized_order = OrderSerializer(order)
        return Response(serialized_order.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "POST", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def single_order(request, id):
    order = get_object_or_404(Order, id=id)
    if request.method == "GET":
        if (
            request.user != order.user
            and not request.user.groups.filter(name="Manager").exists()
        ):
            return Response(
                {"error": "You are not authorized to view this order."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serialized_order = OrderSerializer(order)
        return Response(serialized_order.data, status=status.HTTP_200_OK)
    if request.method in ["PUT", "PATCH"]:
        if request.user.groups.filter(name="Delivery_crew").exists():
            serialized_order = OrderSerializer(order, data=request.data, partial=True)
            serialized_order.status = 1
            serialized_order.is_valid(raise_exception=True)
            serialized_order.save()
            return Response(serialized_order.data, status=status.HTTP_200_OK)
        if (
            request.user != order.user
            and not request.user.groups.filter(name="Manager").exists()
        ):
            return Response(
                {"error": "You are not authorized to update this order."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serialized_order = OrderSerializer(order, data=request.data)
        serialized_order.is_valid(raise_exception=True)
        serialized_order.save()
        return Response(serialized_order.data, status=status.HTTP_200_OK)


class RatingsView(generics.ListCreateAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return []
        return [IsAuthenticated()]

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])  # se quiser permitir só logados
def categories(request):
    if request.method == 'GET':
        qs = Category.objects.all()
        serializer = CategorySerializer(qs, many=True)
        return Response(serializer.data, status=200)

    if request.method == 'POST':
        serializer = CategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)