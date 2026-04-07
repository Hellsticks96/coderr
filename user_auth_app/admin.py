from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('file', 'location', 'tel', 'description', 'working_hours', 'type')            
        }),
    )
    list_display = ('username', 'email', 'type', 'is_staff', 'is_active')
    list_filter = ('type', 'is_staff')
    search_fields = ('username', 'email')