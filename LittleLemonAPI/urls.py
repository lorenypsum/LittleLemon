from django.urls import path
from . import views

urlpatterns = [
    # path('menu/', views.menu, name='menu'),
    # path('menu', views.MenuList.as_view()),
    path('menu-items/<int:pk>/', views.SingleMenuItemView.as_view()),
    path('menu-items', views.MenuItemsView.as_view()),
]
