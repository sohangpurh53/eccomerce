# Generated by Django 4.2.1 on 2023-08-23 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0023_remove_product_initial_stock'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='stock',
            field=models.PositiveIntegerField(default=0, null=True),
        ),
    ]
