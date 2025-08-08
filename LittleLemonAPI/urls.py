from django.urls import path
from . import views

urlpatterns = [
    # path('menu/', views.menu, name='menu'),
    path('menu', views.MenuList.as_view()),
    path('menu/<int:pk>/', views.Menu.as_view()),
    path('menu-items', views.MenuItemsView.as_view()),
]
