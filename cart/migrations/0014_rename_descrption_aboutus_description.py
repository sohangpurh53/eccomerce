# Generated by Django 4.2.1 on 2023-08-17 12:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0013_remove_order_status_aboutus'),
    ]

    operations = [
        migrations.RenameField(
            model_name='aboutus',
            old_name='descrption',
            new_name='description',
        ),
    ]
