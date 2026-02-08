from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import AuditLog, User, Role
from .forms import UserCreateForm, UserUpdateForm, RoleForm
from django.contrib import messages
from datetime import date
from family_savings.models import MonthlySaving
from django.db.models import Sum, Value
from django.core.paginator import Paginator
from common.constants import MONTHS, MONTH_NUMBERS
from django.db.models.functions import Coalesce
from django.db import models
from users.models import User
from decimal import Decimal

@login_required
def dashboard(request):
    current_year = date.today().year
    year = int(request.GET.get("year", current_year))

    #month wise totals
    monthly_data = (
        MonthlySaving.objects.filter(year=year).values("month").annotate(total=Sum("amount")).order_by("month")
    )

    user_totals = (
        User.objects.filter(is_active=True).annotate(
            total=Coalesce(Sum("savings__amount", filter=models.Q(savings__year=year)), Value(Decimal('0')), output_field=models.DecimalField()
            )).exclude(role__role_name="auditor")
        .order_by("total")
    )
    lowest_paid_member = None
    lowest_paid_amount = 0
    if user_totals.exists():
        lowest_user = user_totals.first()
        lowest_paid_member = lowest_user.first_name
        lowest_paid_amount = lowest_user.total

    month_totals = {m: 0 for m in MONTH_NUMBERS}
    for item in monthly_data:
        month_totals[item["month"]] = item["total"] or 0

    total_yearly = sum(month_totals.values())
    avg_monthly = total_yearly/12 if total_yearly else 0
    highest_month = MONTHS[max(month_totals, key=month_totals.get)-1][1]
    lowest_month = MONTHS[min(month_totals, key=month_totals.get)-1][1]

    years = list(range(current_year, 2020, -1))
    return render(request, 'users/dashboard.html', {
        "months": MONTHS,
        "year": year,
        "years": years,
        "month_totals": month_totals,
        "total_yearly": total_yearly,
        "avg_monthly": round(avg_monthly, 2),
        "highest_month": highest_month,
        "lowest_month": lowest_month,
        "lowest_paid_member": lowest_paid_member,
        "lowest_paid_amount": lowest_paid_amount
    })

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            AuditLog.objects.create(
                user=user,
                action="User logged in"
            )
            login(request, user)
            return redirect("dashboard")
        else:
            return render(request, "users/login.html", {"error": "Invalid credentials"})
        
    return render(request, "users/login.html")

def user_logout(request):
    if request.user.is_authenticated:
        AuditLog.objects.create(
            user=request.user,
            action="User logged out"
        )
    logout(request)    
    return redirect("login")

# @login_required
# def dashboard(request):
#     return render(request, "users/dashboard.html")

def is_admin(user):
    return user.role and user.role.role_name == 'admin'

def is_auditor(user):
    return user.role and user.role.role_name == 'auditor'

@login_required
def admin_only_view(request):
    if not is_admin(request.user):
        return HttpResponseForbidden("Access Denied")
    return HttpResponse("Admin Access Granted")

@login_required
def auditor_view(request):
    if is_auditor(request.user):
        return HttpResponse("Read-only Access")
    return HttpResponse("User is not an auditor")

@login_required
def user_list(request):
    if not (is_admin(request.user) or is_auditor(request.user)):
        return HttpResponseForbidden("Access Denied")
    
    users = User.objects.all()
    return render(request, "users/user_list.html", {"users": users})

@login_required
def user_create(request):
    if not is_admin(request.user):
        return HttpResponseForbidden("Admins only can access")
    
    form = UserCreateForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        messages.success(request, f"User {user.username} created successfully.")
        return redirect("user_list")
    
    return render(request, "users/user_form.html", {"form": form})


@login_required
def user_update(request, pk):
    if not is_admin(request.user):
        return HttpResponseForbidden("Admins only can access")
    
    user = get_object_or_404(User, pk=pk)
    form = UserUpdateForm(request.POST or None, instance=user)

    if form.is_valid():
        user = form.save()
        messages.success(request, f"User {user.username} updated successfully.")
        return redirect("user_list")
    
    return render(request, "users/user_form.html", {"form": form})

# @login_required
# def user_delete(request, pk):
#     if not is_admin(request.user):
#         return HttpResponseForbidden("Admins only can access")
    
#     user = get_object_or_404(User, pk=pk)
#     user.delete()
#     return redirect("user_list")

@login_required
def user_toggle_status(request, pk):
    if not is_admin(request.user):
        return HttpResponseForbidden("Admins only can access")
    
    user = get_object_or_404(User, pk=pk)

    #prevent admin from deactivating himself
    if user==request.user:
        messages.warning(request, "You cannot deactivated your own account.")
        return redirect("user_list")
    
    user.is_active = not user.is_active  
    
    messages.success(request, f"User {user.username} {'activated' if user.is_active else 'deactivated'} successfully.")
    user.save()
    return redirect("user_list")

@login_required
def role_list(request):
    if not (is_admin(request.user) or is_auditor(request.user)):
        return HttpResponseForbidden("Access Denied")
    
    roles = Role.objects.all()
    return render(request, "users/role_list.html", {"roles": roles})

@login_required
def role_create(request):
    if not is_admin(request.user):
        return HttpResponseForbidden("Admins only can access")
    
    form = RoleForm(request.POST or None)
    if form.is_valid():
        role = form.save()
        messages.success(request, f"Role {role.role_name} created successfully")
        return redirect("role_list")
    
    return render(request, "users/role_form.html", {"form": form})

@login_required
def role_update(request, pk):
    if not is_admin(request.user):
        return HttpResponseForbidden("Admins only can access")
    
    role = get_object_or_404(Role, pk=pk)
    form = RoleForm(request.POST or None, instance=role)
    if form.is_valid():
        form.save()
        messages.success(request, f"Role {role.role_name} created successfully")
        return redirect("role_list")
    
    return render(request, "users/role_form.html", {"form": form})

@login_required
def role_delete(request,pk):
    if not is_admin(request.user):
        return HttpResponseForbidden("Admins only can delete")
    
    role = get_object_or_404(Role, pk=pk)
    
    if role.users.exists():
        messages.error(request, "Role is assigned to users and cannot be deleted.")
        return redirect("role_list")
    
    role.delete()
    messages.success(request, "Role deleted successfully.")
    return redirect("role_list")

@login_required
def audit_logs(request):
    if request.user.role.role_name not in ['auditor', 'admin']:
        return HttpResponseForbidden("Access Denied")

    logs = AuditLog.objects.select_related("user").order_by("-timestamp")
    paginator = Paginator(logs, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # return HttpResponse(request, "users/audit_logs.html", {"logs": logs})
    return render(request, "users/audit_logs.html", {
        "page_obj": page_obj
    })