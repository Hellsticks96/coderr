from django.contrib import admin

from orders.models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'business_user', 'customer_user', 'status', 'created_at')
    search_fields = ('business_user__username', 'customer__username')
    list_filter = ('status',)