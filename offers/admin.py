from django.contrib import admin

from offers.models import Detail, Package


class DetailInline(admin.TabularInline):
    model = Detail
    extra = 1


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "created_at", "updated_at")
    search_fields = ("title", "user__username")
    inlines = [DetailInline]


@admin.register(Detail)
class DetailAdmin(admin.ModelAdmin):
    list_display = ("title", "package", "price", "delivery_time_in_days", "offer_type")
    search_fields = ("title", "package__title")
    list_filter = ("offer_type",)
