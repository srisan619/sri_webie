from django.urls import path
from .views import family_savings_view, save_monthly_saving, savings_audit_log, export_audit_logs

urlpatterns = [
    path("", family_savings_view, name="family_savings"),
    path("save/", save_monthly_saving, name="save_monthly_saving"),
    path("audit-logs/", savings_audit_log, name="savings_audit_log"),
    path("audit-logs/export", export_audit_logs, name="export_audit_logs")
]