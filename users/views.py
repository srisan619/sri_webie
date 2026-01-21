from django.shortcuts import render
from django.http import HttpResponse

def dashboard(request):
    if request.user.is_authenticated and request.user.role:
        if request.user.role.role_name == "admin":
            return HttpResponse("Welcome Admin")
        elif request.user.role.role_name == "auditor":
            return HttpResponse("Welcome Auditor(Read only)")
    return HttpResponse("Welcome user")
