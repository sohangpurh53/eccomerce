# Generated by Django 4.2.1 on 2023-08-17 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0011_rename_payment_status_order_is_paid'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
