from django import forms
from .models import User, Role
from django.contrib.auth.forms import UserCreationForm

class UserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "role", "is_active"]
        

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "role", "is_active"]

class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ["role_name", "description"]