# Generated by Django 4.2.1 on 2023-08-26 14:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0030_alter_order_shippping_address'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='shippping_address',
            new_name='shipping_address',
        ),
    ]
