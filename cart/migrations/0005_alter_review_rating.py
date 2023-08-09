# Generated by Django 4.2.1 on 2023-07-31 13:07

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0004_product_initial_stock'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='rating',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1, message='Rating should not be less than 1.'), django.core.validators.MaxValueValidator(5, message='Rating should not be greater than 5.')]),
        ),
    ]
