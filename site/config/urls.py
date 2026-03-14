
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from products.views import (
    index,
    catalog,
    product_detail,
    cart_view,
    add_to_cart,
    remove_from_cart,
    clear_cart,
    checkout,
    register,
    account,
    logout_view,
    remove_avatar,
    save_cropped_avatar,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='home'),
    path('catalog/', catalog, name='catalog'),
    path('product/<int:product_id>/', product_detail, name='product_detail'),
    path('cart/', cart_view, name='cart'),
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', clear_cart, name='clear_cart'),
    path('checkout/', checkout, name='checkout'),
    path('account/', account, name='account'),
    path('account/remove-avatar/', remove_avatar, name='remove_avatar'),
    path('account/save-avatar/', save_cropped_avatar, name='save_cropped_avatar'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register, name='register'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
