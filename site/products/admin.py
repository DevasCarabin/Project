
from django.contrib import admin
from .models import Order, OrderItem, Product, Profile


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)
    list_filter = ('price',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('price',)
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'total', 'status')
    list_filter = ('created_at', 'status')
    search_fields = ('user__username',)
    readonly_fields = ('total',)
    inlines = [OrderItemInline]
    actions = ['mark_shipped', 'mark_completed']

    def mark_shipped(self, request, queryset):
        updated = queryset.update(status=Order.STATUS_SHIPPED)
        self.message_user(request, f"Отмечено как отправленные: {updated} заказов.")
    mark_shipped.short_description = 'Отметить как отправленные'

    def mark_completed(self, request, queryset):
        updated = queryset.update(status=Order.STATUS_COMPLETED)
        self.message_user(request, f"Отмечено как завершённые: {updated} заказов.")
    mark_completed.short_description = 'Отметить как завершённые'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    search_fields = ('product__name',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'avatar')
    search_fields = ('user__username',)
