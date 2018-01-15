from django.contrib import admin

# Register your models here.

from .models import Client, ClientPayment, Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 3

class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]

    list_display = ('client', 'date', 'find_total_price', 'get_item_list')

class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_balance')

class ClientPaymentAdmin(admin.ModelAdmin):
    list_display = ('client', 'date', 'amount_CNY')
admin.site.register(Client, ClientAdmin)
admin.site.register(ClientPayment, ClientPaymentAdmin)
admin.site.register(Order, OrderAdmin)
# admin.site.register(OrderItem)
