from .views import _get_cart


def cart_count(request):
    cart = _get_cart(request)
    total_items = sum(item.get('quantity', 0) for item in cart.values())
    return {'cart_count': total_items}
