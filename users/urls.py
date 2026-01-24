from django.urls import path
from .views import dashboard, user_login, user_logout, user_list

urlpatterns=[
    path('dashboard/', dashboard, name="dashboard"),
    path('login/', user_login, name="login"),
    path('logout/', user_logout, name="logout"),
    path('users/', user_list, name="user_list"),
]