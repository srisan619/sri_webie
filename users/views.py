from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import AuditLog

def dashboard(request):
    if request.user.is_authenticated and request.user.role:
        if request.user.role.role_name == "admin":
            return HttpResponse("Welcome Admin")
        elif request.user.role.role_name == "auditor":
            return HttpResponse("Welcome Auditor(Read only)")
    return HttpResponse("Welcome user")

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

@login_required
def dashboard(request):
    return render(request, "users/dashboard.html")

def is_admin(user):
    return user.role and user.role.role_name == 'admin'

def is_auditor(user):
    return user.role and user.role.role_name == 'auditor'

@login_required
def admin_only_view(request):
    if not is_admin(request.user):
        return HttpResponse("Access Denied", status=403)
    return HttpResponse("Admin Access Granted")

@login_required
def auditor_view(request):
    if is_auditor(request.user):
        return HttpResponse("Read-only Access")
    return HttpResponse("User is not an auditor")

@login_required
def audit_logs(request):
    if not is_auditor(request.user):
        return HttpResponse("Access Denied", status=403)

    logs = AuditLog.objects.all()
    return HttpResponse(request, "users/audit_logs.html", {"logs": logs})
