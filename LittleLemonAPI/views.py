from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import generics
from .models import MenuItem
from .serializers import MenuItemSerializer

# Create your views here.
@api_view(['GET', 'POST'])
def menu(request):
    return Response("List of menu items", status=status.HTTP_200_OK)

class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView, generics.DestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

# class MenuList(APIView):
#     def get(self, request):
#         return Response({"message": "List of menu items"}, status=status.HTTP_200_OK)

#     def post(self, request):
#         return Response({"message": "Menu item created"}, status=status.HTTP_201_CREATED)

# class Menu(APIView):
#     def get(self, request, pk):
#         return Response({"message": f"Details of menu item {pk}"}, status=status.HTTP_200_OK)
    
#     def put(self, request, pk):
#         return Response({"title": request.data.get("title", "")}, status=status.HTTP_200_OK)