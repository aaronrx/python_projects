# Generated by Django 3.0.2 on 2020-01-22 02:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pizzas', '0002_auto_20200122_0251'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='topping',
            options={'verbose_name_plural': 'toppings'},
        ),
    ]
