from django.contrib import admin
from django.contrib.auth.models import User
from user_auth_app.models import UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'profile'

class CustomUserAdmin(admin.ModelAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'is_staff', 'is_active')
    search_fields = ('username', 'email')

from django.contrib.auth.admin import UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'created_at')
    search_fields = ('user__username', 'user__email', 'type')
    list_filter = ('type',)