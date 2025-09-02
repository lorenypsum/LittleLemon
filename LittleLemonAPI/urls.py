from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
   # Menu items
    path('menu-items/', views.menu_items),
    path('menu-items/<int:id>/', views.single_item),

    # Categories
    path('categories/', views.categories),
    #path('categories/<int:id>/', views.single_category),

    # Cart
    path('cart/', views.cart),

    # Orders
    path('orders/', views.orders),
    path('orders/<int:id>/', views.single_order),

    # Groups - Manager
    path('groups/manager/users/', views.managers),
    path('groups/manager/users/<int:id>/', views.single_manager),

    # Groups - Delivery crew
    path('groups/delivery-crew/users/', views.delivery_crew),
    path('groups/delivery-crew/users/<int:id>/', views.single_delivery_crew),

    # Auth
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),

    # Throttle check
    path('throttle-check/', views.throttle_check),
    path('throttle-check-auth/', views.throttle_check_auth),

    # Ratings
    path('ratings/', views.RatingsView.as_view()),
]