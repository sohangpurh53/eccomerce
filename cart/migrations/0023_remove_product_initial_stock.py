# Generated by Django 4.2.1 on 2023-08-23 09:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0022_remove_product_image_productimage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='initial_stock',
        ),
    ]
