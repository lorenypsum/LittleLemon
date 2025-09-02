from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    # path('menu/', views.menu, name='menu'),
    # path('menu', views.MenuList.as_view()),
    path('menu-items/', views.menu_items),
    path('menu-items/<int:id>', views.single_item),
    path('secret/', views.secret),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('manager-view/', views.manager_view),
    path('throttle-check/', views.throttle_check),
    path('throttle-check-auth/', views.throttle_check_auth),
    path('groups/managers/users', views.managers),
    path('ratings/', views.RatingsView.as_view()),
]
# ee5bde21a9638fc4a2fd5cb5807a5932090034b2
# eb5cf167d7d9ff71edeff6fc9e8dbc95a1f62f43