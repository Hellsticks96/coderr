from django.contrib import admin
from reviews.models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'business_user', 'reviewer', 'rating', 'created_at')
    search_fields = ('business_user__username', 'reviewer__username')
    list_filter = ('rating',)