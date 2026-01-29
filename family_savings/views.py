from django.shortcuts import render
from .models import FamilyMember, MonthlySaving
from users.models import User
from django.contrib.auth.decorators import login_required
from users.views import is_auditor

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