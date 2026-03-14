from django.db import migrations


def create_profiles(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Profile = apps.get_model('products', 'Profile')
    for user in User.objects.all():
        if not hasattr(user, 'profile'):
            Profile.objects.create(user=user)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_order_status'),
    ]

    operations = [
        migrations.RunPython(create_profiles, noop),
    ]
