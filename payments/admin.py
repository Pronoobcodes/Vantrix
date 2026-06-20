from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'reference',
        'user',
        'order',
        'gateway',
        'amount',
        'currency',
        'status',
        'timestamp',
    )
    list_filter = ('status', 'gateway', 'currency')
    search_fields = ('reference', 'gateway_reference', 'user__username', 'order__id')
    readonly_fields = ('id', 'timestamp', 'gateway_response')
    raw_id_fields = ('user', 'order')
