from django.contrib import admin
from .models import Payment, PaymentRefund


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_id', 'user', 'amount', 'currency',
        'status', 'payment_method', 'created_at'
    ]
    list_filter = ['status', 'payment_method', 'currency', 'created_at']
    search_fields = ['transaction_id', 'user__username', 'user__email']
    readonly_fields = [
        'payment_id', 'transaction_id', 'ssl_session_id',
        'ssl_transaction_id', 'gateway_response', 'created_at',
        'updated_at', 'paid_at'
    ]

    fieldsets = (
        (None, {
            'fields': ('payment_id', 'user', 'booking', 'premium_service')
        }),
        ('Payment Details', {
            'fields': ('amount', 'currency', 'status', 'payment_method')
        }),
        ('SSL Commerz Details', {
            'fields': ('transaction_id', 'ssl_session_id', 'ssl_transaction_id'),
            'classes': ('collapse',)
        }),
        ('Gateway Response', {
            'fields': ('gateway_response',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'paid_at'),
            'classes': ('collapse',)
        })
    )

    def has_add_permission(self, request):
        return False  # Payments should only be created through the system

    def has_delete_permission(self, request, obj=None):
        return False  # Don't allow deletion of payment records


@admin.register(PaymentRefund)
class PaymentRefundAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'get_transaction_id', 'get_user', 'refund_amount',
        'status', 'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['payment__transaction_id', 'payment__user__username']
    readonly_fields = ['created_at', 'processed_at']

    def get_transaction_id(self, obj):
        return obj.payment.transaction_id
    get_transaction_id.short_description = 'Transaction ID'

    def get_user(self, obj):
        return obj.payment.user.get_full_name() or obj.payment.user.username
    get_user.short_description = 'User'

    fieldsets = (
        (None, {
            'fields': ('payment', 'refund_amount', 'reason')
        }),
        ('Processing', {
            'fields': ('status', 'refund_reference')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'processed_at'),
            'classes': ('collapse',)
        })
    )
