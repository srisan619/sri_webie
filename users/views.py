from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import AuditLog, User, Role
from .forms import UserCreateForm, UserUpdateForm, RoleForm
from django.contrib import messages

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'users/dashboard.html')

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
        return HttpResponseForbidden("Access Denied")
    return HttpResponse("Admin Access Granted")

@login_required
def auditor_view(request):
    if is_auditor(request.user):
        return HttpResponse("Read-only Access")
    return HttpResponse("User is not an auditor")

@login_required
def audit_logs(request):
    if not is_auditor(request.user):
        return HttpResponseForbidden("Access Denied")

    logs = AuditLog.objects.all()
    return HttpResponse(request, "users/audit_logs.html", {"logs": logs})

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