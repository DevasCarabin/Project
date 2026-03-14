
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse


class Product(models.Model):
    name = models.CharField('Название', max_length=200)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    description = models.TextField('Описание', blank=True)
    image = models.ImageField('Фото', upload_to='products/', blank=True, null=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.pk])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Автоматически обрезаем / масштабируем загруженное изображение до квадратного вида
        if self.image:
            try:
                from PIL import Image, ImageOps

                img_path = self.image.path
                with Image.open(img_path) as img:
                    img = ImageOps.exif_transpose(img)
                    img = ImageOps.fit(img, (1200, 1200), Image.LANCZOS)
                    img.save(img_path, quality=85)
            except Exception:
                # Если Pillow не установлен или возникли ошибки, пропускаем.
                pass


class Profile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField('Аватар', upload_to='avatars/', blank=True, null=True)

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return f'Профиль {self.user.username}'


@receiver(post_save, sender=get_user_model())
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=get_user_model())
def save_user_profile(sender, instance, **kwargs):
    # Ensure a profile exists before attempting to save it. This handles
    # legacy users who were created before the Profile model existed.
    try:
        profile = instance.profile
    except sender.profile.RelatedObjectDoesNotExist:  # pragma: no cover
        profile = Profile.objects.create(user=instance)
    else:
        # if it existed, just save in case some fields changed indirectly
        profile.save()


class Order(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_SHIPPED = 'shipped'
    STATUS_COMPLETED = 'completed'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'В обработке'),
        (STATUS_SHIPPED, 'Отправлен'),
        (STATUS_COMPLETED, 'Завершён'),
    ]

    created_at = models.DateTimeField('Дата заказа', auto_now_add=True)
    user = models.ForeignKey(
        'auth.User',
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='orders',
    )
    total = models.DecimalField('Сумма', max_digits=10, decimal_places=2, default=0)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заказ #{self.pk} ({self.get_status_display()}) — {self.user.username}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name='Заказ', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, verbose_name='Товар', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField('Количество', default=1)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

    def __str__(self):
        return f'{self.product.name} — {self.quantity} шт.'
