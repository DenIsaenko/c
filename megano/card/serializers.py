import random

from rest_framework import serializers

from shop.models import Product
from shop.serializers import (
    ProductSerializer,
    CategorySerializer,
    ProductImageSerializer,
    TagSerializer,
    ReviewSerializer,
)
from .cart import Cart
from .models import Order, Payment, PaymentType, Status, OrderItem


class PaymentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentType
        fields = ["id", "name"]


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ["id", "name"]


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = OrderItem
        fields = ["id", "product", "price", "quantity"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation["product"]


class OrderSerializer(serializers.ModelSerializer):
    fullName = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    totalCost = serializers.SerializerMethodField()
    paymentType = serializers.CharField(source="paymentType.name")
    status = serializers.CharField(source="status.name")
    products = OrderItemSerializer(source="items", many=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "createdAt",
            "fullName",
            "email",
            "phone",
            "paymentType",
            "totalCost",
            "status",
            "city",
            "address",
            "products",
        )

    def get_fullName(self, obj):
        return obj.user.fullName

    def get_email(self, obj):
        return obj.user.email

    def get_phone(self, obj):
        return str(obj.user.phone)

    def get_totalCost(self, obj):
        return obj.get_total_price()

    def get_products(self, obj):
        order_items = obj.items.all()
        product_serializer = ProductSerializer(order_items.values("product"), many=True)
        return product_serializer.data


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["paymentType", "number", "name", "month", "year", "code"]

    def create(self, validated_data):
        payment_type = validated_data.get("paymentType")
        if payment_type == "someone":
            validated_data["number"] = str(random.randint(10000000, 99999999))
            validated_data["name"] = "Random User"
            validated_data["month"] = str(random.randint(1, 12)).zfill(2)
            validated_data["year"] = str(random.randint(2022, 2030))
            validated_data["code"] = str(random.randint(100, 999))
        return super().create(validated_data)
