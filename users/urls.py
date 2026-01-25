from django.urls import path
from .views import dashboard, user_login, user_logout, user_list,user_create,user_update,user_toggle_status#, user_delete

urlpatterns=[
    path('', dashboard, name="home"),
    path('dashboard/', dashboard, name="dashboard"),
    path('login/', user_login, name="login"),
    path('logout/', user_logout, name="logout"),
    path('users/', user_list, name="user_list"),
    path('users/create/', user_create, name="user_create"),
    path('users/<pk>/edit/', user_update, name="user_update"),
    # path('users/<pk>/delete/', user_delete, name="user_delete"),
    path('users/<pk>/toggle-status/', user_toggle_status, name="user_toggle_status")
]