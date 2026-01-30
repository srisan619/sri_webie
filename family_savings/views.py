from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import MonthlySaving
from users.models import User
from django.contrib.auth.decorators import login_required
from users.views import is_auditor
from decimal import Decimal

@login_required
def family_savings_view(request):
    MONTHS = [
        (1, 'Jan'), (2, 'Feb'),(3, 'Mar'), (4, 'Apr'), (5, 'May'), (6, 'Jun'), (7, 'Jul'), (8, 'Aug'), (9, 'Sep'), (10, 'Oct'), (11, 'Nov'), (12, 'Dec')
    ]
    year = int(request.GET.get("year", 2025))

    users = User.objects.filter(
        is_active=True
    ).exclude(role__role_name="auditor")

    data = []

    for user in users:
        row = {"user": user, "months": {}, "total": 0}

        for m in range(1,13):
            saving = MonthlySaving.objects.filter(
                user=user, year=year, month=m
            ).first()
            amount = saving.amount if saving else 0
            row["months"][m] = amount
            row["total"] += amount
        
        data.append(row)
    
    return render(request, "family_savings/table.html", {
        "data": data,
        "year": year,
        "months": MONTHS,
        "is_readonly": is_auditor(request.user)
    })

@require_POST
@login_required
def save_monthly_saving(request):
    if is_auditor(request.user):
        return JsonResponse({"error": "Read-only access"}, status=403)
    
    user_id = request.POST.get('user_id')
    month = int(request.POST.get('month'))
    year = int(request.POST.get('year'))
    amount = Decimal(request.POST.get('amount', 0))

    saving, created = MonthlySaving.objects.get_or_create(
        user_id=user_id,
        year=year,
        month = month,
        defaults={"amount": amount}
    )

    if not created:
        saving.amount = amount
        saving.save()

    return JsonResponse({
        "success": True,
        "amount": str(saving.amount)
    })