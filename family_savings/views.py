from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseForbidden
from .models import MonthlySaving, SavingsAuditLog
from users.models import User
from django.contrib.auth.decorators import login_required
from users.views import is_auditor, is_admin
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
        "is_admin": is_admin(request.user)
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
    affected_user = User.objects.get(id=user_id)
    saving, created = MonthlySaving.objects.get_or_create(
        user_id=user_id,
        year=year,
        month = month,
        defaults={"amount": amount}
    )

    old_amount = saving.amount if not created else 0
    if old_amount != amount:
        saving.amount = amount
        saving.save()

        SavingsAuditLog.objects.create(
            changed_by=request.user,
            affected_by = affected_user,
            year=year,
            month=month,
            old_amount=old_amount,
            new_amount=amount
        )

    return JsonResponse({
        "success": True,
        "amount": str(saving.amount)
    })

@login_required
def savings_audit_log(request):
    if not is_admin(request.user):
        return HttpResponseForbidden("Access Denied")
    
    logs = SavingsAuditLog.objects.select_related(
        "changed_by", "affected_by"
    ).order_by("changed_at")

    return render(request, "family_savings/audit_logs.html", {"logs": logs})