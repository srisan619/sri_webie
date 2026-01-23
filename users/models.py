from django.db import models
from django.contrib.auth.models import AbstractUser

class Role(models.Model):
    role_name =models.CharField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.role_name

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class User(AbstractUser):
    role = models.ForeignKey(Role, on_delete=models.PROTECT, null=True, blank=True)
    groups = models.ManyToManyField('auth.Group', related_name='custom_user_set', blank=True, help_text='The groups this user belongs to', verbose_name='groups')
    user_permissions = models.ManyToManyField('auth.Permission', related_name='custom_user_set', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions')

class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action}"