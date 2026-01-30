from django.urls import path
from .views import family_savings_view, save_monthly_saving

urlpatterns = [
    path("", family_savings_view, name="family_savings"),
    path("save/", save_monthly_saving, name="save_monthly_saving")
]