from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from django.contrib.auth.models import User, Group
from rest_framework import status, generics, viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from .models import MenuItem, Rating
from .serializers import MenuItemSerializer, RatingSerializer
from .throttles import TenCallsPerMinute



# Create your views here.
@api_view(['GET', 'POST'])
def menu_items(request):
    if request.method == 'GET':
        items = MenuItem.objects.select_related('category').all()
        category_name = request.query_params.get('category')
        to_price = request.query_params.get('to_price')
        search = request.query_params.get('search')
        ordering = request.query_params.get('ordering')
        perpage = request.query_params.get('perpage', default = 2)
        page = request.query_params.get('page', default = 1)
        
        if category_name:
            items = items.filter(category__title=category_name)
        if to_price:
            items = items.filter(price__lte=to_price)
        if search:
            items = items.filter(title__contains=search)
        if ordering:
            ordering_fields = ordering.split(',')
            items = items.order_by(*ordering_fields)

        paginator = Paginator(items, per_page = perpage)
        try: 
            items = paginator.page(number=page)
        except EmptyPage:
            items = []           
        serialized_item = MenuItemSerializer(items, many=True)
        return Response(serialized_item.data)
    if request.method == 'POST':
        serialized_item = MenuItemSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()
        return Response(serialized_item.data, status= status.HTTP_201_CREATED)

@api_view()
def single_item(request, id):
    item = get_object_or_404(MenuItem, id=id)
    serialized_item = MenuItemSerializer(item)
    return Response(serialized_item.data)

@api_view()
@permission_classes([IsAuthenticated])
def secret(request):
    return Response({"message": "This is a secret message!"})

@api_view()
@permission_classes([IsAuthenticated])
def manager_view(request):
    if request.user.groups.filter(name='Manager').exists():
        return Response({"message": "This is a manager view!"})
    else:
        return Response({"message": "You are not authorized to view this page."}, status=status.HTTP_403_FORBIDDEN)
    
@api_view()
@throttle_classes([AnonRateThrottle])
def throttle_check(request):
    return Response({"message": "This is a throttled view!"})

@api_view()
@permission_classes([IsAuthenticated])
@throttle_classes([TenCallsPerMinute])
def throttle_check_auth(request):
    return Response({"message": "This is a throttled view for authenticated users!"})

@api_view(['POST'])
@permission_classes([IsAdminUser])
def managers(request):
    username = request.data.get('username')
    if username:
        user = get_object_or_404(User, username=username)
        managers = Group.objects.get(name='Manager')
        if request.method == 'POST':
            managers.user_set.add(user)
        elif request.method == 'DELETE':
            managers.user_set.remove(user)
        return Response({"message": "ok"})
    return Response({"error": "Username not provided."}, status=status.HTTP_400_BAD_REQUEST)

class RatingsView(generics.ListCreateAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return []
        return [IsAuthenticated()]