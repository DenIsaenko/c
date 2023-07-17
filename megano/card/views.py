import json
import random

from django.utils import timezone
from django.shortcuts import render, redirect
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from shop.models import Product
from shop.serializers import ProductSerializer

from .models import Order, PaymentType, Status, OrderItem
from django.contrib import messages
from .cart import Cart
from .serializers import OrderSerializer, PaymentSerializer
from django.db.models import Avg, Count

# class CartView(APIView):
#     def get(self, request):
#         products = Product.objects.filter(count__gt=1)  # Фильтрация только товаров с count > 1
#         serializer = ProductSerializer(products, many=True)
#         return Response(serializer.data)
#
#     def post(self, request):
#         product_id = request.data.get('id')
#         try:
#             product = Product.objects.get(id=product_id)
#             product.count += 1
#             product.save()
#             response_data = {
#                 'id': product.id,
#                 'count': product.count
#             }
#             return Response(response_data, status=200)
#         except Product.DoesNotExist:
#             return Response({'error': 'Product not found'}, status=404)
# class CartView(APIView):
#     def get(self, request):
#         cart, created = Cart.objects.get_or_create(user=request.user)
#         products = cart.product.all()  # Обратитесь к связанному менеджеру
#         serializer = ProductSerializer(products, many=True)
#         return Response(serializer.data)
#
#     def post(self, request):
#         product_id = request.data.get('id')
#         try:
#             product = Product.objects.get(id=product_id)
#             product.count += 1
#             product.save()
#
#             cart, created = Cart.objects.get_or_create(user=request.user)
#             cart.product.add(product)  # Используйте метод add() для добавления нового товара
#
#             response_data = {
#                 'id': product.id,
#                 'count': product.count
#             }
#             return Response(response_data, status=200)
#         except Product.DoesNotExist:
#             return Response({'error': 'Product not found'}, status=404)
#
#     def delete(self, request):
#         product_id = request.data.get('id')
#         try:
#             product = Product.objects.get(id=product_id)
#
#             cart, created = Cart.objects.get_or_create(user=request.user)
#             cart.product.remove(product)  # Удаление продукта из корзины
#
#             # Обновление значения count до 0 при удалении продукта из корзины
#             Product.objects.filter(id=product_id).update(count=0)
#
#             response_data = {
#                 'message': 'Product removed from cart successfully'
#             }
#             return Response(response_data, status=200)
#         except Product.DoesNotExist:
#             return Response({'error': 'Product not found'}, status=404)
#


class CartDetailView(APIView):
    """APIView для корзины, реализация методов get, post и delete"""

    def get_cart_items(self, cart):
        cart_items = []
        for item in cart:
            product = Product.objects.get(id=item["product_id"])

            cart_items.append(
                {
                    "id": product.id,
                    "category": product.category.id,
                    "price": float(item["price"]),
                    "count": item["quantity"],
                    "date": product.date.strftime("%a %b %d %Y %H:%M:%S GMT%z (%Z)"),
                    "title": product.title,
                    "description": product.description,
                    "freeDelivery": product.freeDelivery,
                    "images": [
                        {"src": image.src.url, "alt": image.alt}
                        for image in product.images.all()
                    ],
                    "tags": [
                        {"id": tag.id, "name": tag.name} for tag in product.tags.all()
                    ],
                    "reviews": 4,
                    "rating": product.rating,
                }
            )
        return cart_items

    def get(self, request):
        cart = Cart(request)
        cart_items = self.get_cart_items(cart)
        return Response(cart_items)

    def post(self, request):
        product_id = request.data.get("id")
        quantity = int(request.data.get("count", 1))

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        cart = Cart(request)
        cart.add(product, quantity)
        cart_items = self.get_cart_items(cart)
        return Response(cart_items)

    def delete(self, request):
        product_id = request.data.get("id")
        quantity = request.data.get("count", 1)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        cart = Cart(request)
        cart.remove(product, quantity)
        cart_items = self.get_cart_items(cart)
        return Response(cart_items)


class OrdersView(APIView):
    def get(self, request):
        user = request.user.profile
        orders = Order.objects.filter(user=user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=200)

    def post(self, request):
        cart = Cart(request)
        products = request.data  # Получаем список объектов товаров из запроса

        city = None
        address = None
        if isinstance(products, list) and len(products) > 0:
            first_product = products[0]
            city = first_product.get(
                "city", None
            )  # Получаем значение поля city из первого объекта товара
            address = first_product.get(
                "address", None
            )  # Получаем значение поля address из первого объекта товара

        payment_type = PaymentType.objects.first()
        status = Status.objects.first()

        order = Order.objects.create(
            user=request.user.profile,
            createdAt=timezone.now(),
            paymentType=payment_type,
            status=status,
            city=city,
            address=address,
            paid=False,
            receipt=None,
        )

        total_cost = 0

        for product_data in products:
            product_id = product_data["id"]
            product = Product.objects.get(id=product_id)
            quantity = product_data["count"]

            OrderItem.objects.create(
                order=order, product=product, price=product.price, quantity=quantity
            )
            total_cost += float(product.price) * quantity

        order.total_cost = total_cost
        order.save()

        cart.clear()

        return Response({"orderId": order.id}, status=200)


class OrderDetailView(APIView):
    def get(self, request, id):
        try:
            order = Order.objects.get(id=id)
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=200)
        except Order.DoesNotExist:
            return Response({"message": "Order not found"}, status=404)

    def post(self, request, id):
        cart = Cart(request)
        products = request.data.get("products", [])

        city = request.data.get("city", None)
        address = request.data.get("address", None)

        payment_type = PaymentType.objects.first()
        status = Status.objects.first()

        order = Order.objects.create(
            user=request.user.profile,
            createdAt=timezone.now(),
            paymentType=payment_type,
            status=status,
            city=city,
            address=address,
            paid=False,
            receipt=None,
        )

        total_cost = 0

        for product_data in products:
            product_id = product_data["id"]
            product = Product.objects.get(id=product_id)
            quantity = product_data["count"]

            order_item = OrderItem(
                order=order, product=product, price=product.price, quantity=quantity
            )
            order_item.save()
            total_cost += float(product.price) * quantity

        order.totalCost = total_cost
        order.save()

        cart.clear()

        return Response({"orderId": order.id}, status=200)


class PaymentView(APIView):
    def post(self, request, id):
        order = Order.objects.get(id=id)
        payment_data = request.data

        payment_type = payment_data.get("paymentType")
        if payment_type == "someone":
            card_number = str(random.randint(10000000, 99999999))
            card_name = "Random User"
            card_month = str(random.randint(1, 12)).zfill(2)
            card_year = str(random.randint(2022, 2030))
            card_code = str(random.randint(100, 999))
        else:
            card_number = payment_data.get("number")
            card_name = payment_data.get("name")
            card_month = payment_data.get("month")
            card_year = payment_data.get("year")
            card_code = payment_data.get("code")

        payment_result = self.process_payment(
            payment_type,
            card_number,
            card_name,
            card_month,
            card_year,
            card_code,
            order,
        )
        if payment_result:
            return Response(status=200)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def process_payment(
        self,
        payment_type,
        card_number,
        card_name,
        card_month,
        card_year,
        card_code,
        order,
    ):
        if payment_type == "someone" or (
            card_number.isdigit()
            and len(card_number) <= 8
            and int(card_number) % 2 == 0
        ):
            # Логика для успешной оплаты
            order.paid = True
            order.save()
            return True
        return False
