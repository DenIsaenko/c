from django.db import models

from django.contrib.auth.models import User
from shop.models import Product
from myauth.models import Profile


class PaymentType(models.Model):
    """Модель для типов оплаты"""

    name = models.CharField(max_length=100, unique=True, verbose_name="Тип оплаты")


class Status(models.Model):
    """Модель статусов заказов"""

    name = models.CharField(
        max_length=100, unique=True, verbose_name="Название статуса"
    )


class Order(models.Model):
    """Модель заказа"""

    user = models.ForeignKey(
        Profile, on_delete=models.PROTECT, verbose_name="Заказ от пользователя"
    )
    createdAt = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    paymentType = models.ForeignKey(
        PaymentType, default=1, on_delete=models.PROTECT, verbose_name="Способ оплаты"
    )
    status = models.ForeignKey(
        Status, default=1, on_delete=models.PROTECT, verbose_name="Статус"
    )
    city = models.CharField(max_length=255, verbose_name="Город", blank=True, null=True)
    address = models.TextField(verbose_name="Адрес доставки", blank=True, null=True)
    paid = models.BooleanField(default=False, verbose_name="Оплачено")
    receipt = models.FileField(
        blank=True, null=True, upload_to="orders/receipts/", verbose_name="Счет"
    )

    def get_total_price(self):
        total_price = sum(item.price * item.quantity for item in self.items.all())
        return total_price


class OrderItem(models.Model):
    """Модель содержимого заказа"""

    order = models.ForeignKey(
        Order, related_name="items", on_delete=models.CASCADE, verbose_name="Заказ"
    )
    product = models.ForeignKey(
        Product,
        related_name="order_items",
        on_delete=models.CASCADE,
        verbose_name="Товар",
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")


class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    number = models.CharField(max_length=16)
    name = models.CharField(max_length=100)
    month = models.CharField(max_length=2)
    year = models.CharField(max_length=4)
    code = models.CharField(max_length=3)
