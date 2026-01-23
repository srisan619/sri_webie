from django.contrib import admin
from .models import Role,User,AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'timestamp')
    # readonly_fields = ('user', 'action', 'timestamp')
    # list_filter = ('timestamp', 'action')
    # search_fields = ('user__username', 'action')

admin.site.register(Role)
admin.site.register(User)