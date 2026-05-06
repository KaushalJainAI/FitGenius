from django.contrib import admin

from .models import Subscription


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status', 'trial_ends_at', 'updated_at')
    search_fields = ('user__email', 'user__username')
    list_filter = ('plan', 'status')
