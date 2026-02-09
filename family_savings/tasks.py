from celery import shared_task
from django.core.mail import send_mail
from django.db.models import Sum
from django.utils.timezone import now

from users.models import User
from family_savings.models import MonthlySaving

# monthly statement task
@shared_task
def send_monthly_savings_statement():
    today = now().date()

    #previous month
    year = today.year
    month = today.month - 1 or 12

    #incase of jan month get previous year
    if today.month == 1:
        year -=1

    users = User.objects.filter(is_active=True).exclude(role__role_name="auditor")

    for user in users:
        current_month_amount = (
            MonthlySaving.objects.filter(user=user, year=year, month=month).aggregate(total=Sum("amount"))["total"] or 0
            )
        current_year_amount = (
            MonthlySaving.objects.filter(user=user, year=year).aggregate(total=Sum("amount"))["total"] or 0
        )

        send_mail(
            subject=f"Monthly Saving Statement - {month}/{year}",
            message=(
                f"Hi {user.first_name},\n\n"
                f"Your monthly savings for {month}/{year} is ₹{current_month_amount}.\n\n"
                f"Your total savings for {year} is ₹{current_year_amount}.\n\n"
                "Thank you."
            ),
            from_email="noreply@aatrust.com",
            recipient_list=[user.email],
            fail_silently=False,
        )