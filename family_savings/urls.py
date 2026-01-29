from django.urls import path
from .views import family_savings_view

urlpatterns = [
    path("", family_savings_view, name="family_savings")
]