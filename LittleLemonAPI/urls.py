from django.urls import path
from . import views

urlpatterns = [
    # path('menu/', views.menu, name='menu'),
    # path('menu', views.MenuList.as_view()),
    path('menu-items/<int:id>/', views.single_item),
    path('menu-items', views.menu_items),
]
