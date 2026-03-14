from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import base64
import io
from PIL import Image
import os

from .forms import ProfileForm, AvatarEditorForm
from .models import Order, OrderItem, Product, Profile

CART_SESSION_KEY = 'cart'


def _get_cart(request):
    return request.session.get(CART_SESSION_KEY, {})


def _save_cart(request, cart):
    request.session[CART_SESSION_KEY] = cart
    request.session.modified = True


def _cart_totals(cart):
    total = 0
    item_count = 0
    for item in cart.values():
        item_count += item.get('quantity', 0)
        total += item.get('line_total', 0)
    return item_count, total


def _build_cart_context(request):
    cart = _get_cart(request).copy()
    items = []
    for product_id, item in cart.items():
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            continue
        quantity = item.get('quantity', 0)
        line_total = product.price * quantity
        items.append({
            'product': product,
            'quantity': quantity,
            'line_total': line_total,
        })
        cart[str(product_id)]['line_total'] = float(line_total)

    item_count, total = _cart_totals(cart)

    return {
        'cart_items': items,
        'cart_total': total,
        'cart_count': item_count,
    }


def index(request):
    products = Product.objects.all()[:6]
    context = {'products': products}
    context.update(_build_cart_context(request))
    return render(request, 'index.html', context)


def catalog(request):
    query = request.GET.get('q', '').strip()
    products = Product.objects.all()
    if query:
        products = products.filter(name__icontains=query)

    context = {
        'products': products,
        'query': query,
    }
    context.update(_build_cart_context(request))
    return render(request, 'catalog.html', context)


def cart_view(request):
    context = _build_cart_context(request)
    return render(request, 'cart.html', context)


def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    context = {'product': product}
    context.update(_build_cart_context(request))
    return render(request, 'product.html', context)


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    qty = int(request.GET.get('qty', 1)) if request.GET.get('qty') else 1
    cart = _get_cart(request).copy()
    key = str(product.id)
    entry = cart.get(key, {'quantity': 0})
    entry['quantity'] = entry.get('quantity', 0) + qty
    cart[key] = entry
    _save_cart(request, cart)
    return redirect(request.GET.get('next') or reverse('cart'))


def remove_from_cart(request, product_id):
    cart = _get_cart(request).copy()
    key = str(product_id)
    if key in cart:
        del cart[key]
        _save_cart(request, cart)
    return redirect(reverse('cart'))


def clear_cart(request):
    _save_cart(request, {})
    return redirect(reverse('cart'))


@login_required
def save_cropped_avatar(request):
    """Save cropped avatar from canvas data"""
    if request.method == 'POST':
        form = AvatarEditorForm(request.POST)
        if form.is_valid():
            avatar_data = form.cleaned_data['avatar_data']
            
            try:
                # Parse base64 image data
                if ',' in avatar_data:
                    avatar_data = avatar_data.split(',')[1]
                
                image_data = base64.b64decode(avatar_data)
                image = Image.open(io.BytesIO(image_data))
                
                # Ensure RGB mode
                if image.mode in ('RGBA', 'P'):
                    image = image.convert('RGB')
                
                # Save to profile
                profile = request.user.profile
                
                # Delete old avatar if exists
                if profile.avatar:
                    profile.avatar.delete(save=False)
                
                # Save new avatar
                from django.core.files.base import ContentFile
                image_io = io.BytesIO()
                image.save(image_io, format='JPEG', quality=90)
                image_io.seek(0)
                
                filename = f'avatar_{request.user.id}.jpg'
                profile.avatar.save(filename, ContentFile(image_io.read()), save=True)
                
                return JsonResponse({'success': True, 'message': 'Аватар сохранён'})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Неверный запрос'}, status=400)


@login_required
def account(request):
    profile = request.user.profile
    form = ProfileForm(request.POST or None, request.FILES or None, instance=profile)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('account')

    context = _build_cart_context(request)
    context.update({
        'profile_form': form,
        'profile': profile,
        'orders': request.user.orders.all(),
    })
    return render(request, 'account.html', context)


@login_required
@require_POST
def remove_avatar(request):
    profile = request.user.profile
    if profile.avatar:
        profile.avatar.delete(save=False)
        profile.avatar = None
        profile.save()
    return redirect('account')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def checkout(request):
    cart = _get_cart(request)
    if not cart:
        return redirect('cart')

    order = Order.objects.create(user=request.user, total=0)
    total = 0

    for product_id, item in cart.items():
        product = Product.objects.filter(pk=product_id).first()
        if not product:
            continue
        quantity = item.get('quantity', 0)
        line_total = product.price * quantity
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=product.price,
        )
        total += line_total

    order.total = total
    order.save()

    _save_cart(request, {})

    return render(request, 'checkout_complete.html', {'order': order})
