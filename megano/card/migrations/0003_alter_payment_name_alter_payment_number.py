# Generated by Django 4.2.2 on 2023-07-02 15:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("card", "0002_alter_order_address_alter_order_city"),
    ]

    operations = [
        migrations.AlterField(
            model_name="payment",
            name="name",
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name="payment",
            name="number",
            field=models.CharField(max_length=16),
        ),
    ]
