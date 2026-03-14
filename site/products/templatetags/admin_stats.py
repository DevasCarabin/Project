from django import template
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum

from products.models import Order, Product

register = template.Library()


@register.simple_tag
def order_stats():
    stats = Order.objects.aggregate(total_orders=Count('id'), total_revenue=Sum('total'))
    user_count = get_user_model().objects.count()
    product_count = Product.objects.count()

    return {
        'orders': stats.get('total_orders') or 0,
        'revenue': stats.get('total_revenue') or 0,
        'users': user_count,
        'products': product_count,
    }
