from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

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
            login(request, user)
            return redirect("dashboard")
        else:
            return render(request, "users/login.html", {"error": "Invalid credentials"})
        
    return render(request, "users/login.html")

def user_logout(request):
    logout(request)
    return redirect("login")

@login_required
def dashboard(request):
    return render(request, "users/dashboard.html")