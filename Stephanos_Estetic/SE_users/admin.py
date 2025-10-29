# SE_users/admin.py
from django.contrib import admin
from .models import Profile, UserOrderHistory

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "display_name", "phone")
    search_fields = ("user__username", "user__email", "display_name", "phone")

@admin.register(UserOrderHistory)
class UserOrderHistoryAdmin(admin.ModelAdmin):
    list_display = ("user", "order", "viewed_at")
    list_filter = ("viewed_at",)
    search_fields = ("user__username", "order__id", "order__customer_email")
    readonly_fields = ("viewed_at",)