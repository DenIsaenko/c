from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer
from .models import (
    Product,
    Category,
    Specification,
    Tag,
    ProductImage,
    Subcategory,
    Review,
)
from django.db.models import Avg, Count


class ProductImageSerializer(ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ("src", "alt")


class SubcategorySerializer(ModelSerializer):
    image = SerializerMethodField()

    class Meta:
        model = Subcategory
        fields = ("id", "title", "image", "category")

    def get_image(self, obj):
        return {"src": obj.image.url, "alt": "hello alt"}


class CategorySerializer(ModelSerializer):
    subcategories = SubcategorySerializer(many=True, read_only=True)
    image = SerializerMethodField()

    class Meta:
        model = Category
        fields = ("id", "image", "title", "subcategories")

    def get_image(self, obj):
        return {"src": obj.image.url, "alt": "hello alt"}


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name")


class SpecificationSerializer(ModelSerializer):
    class Meta:
        model = Specification
        fields = ("name", "value")


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ("author", "email", "text", "rate", "date", "product")


class ProductSerializer(ModelSerializer):
    specifications = SpecificationSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    # category = CategorySerializer(many=False, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    reviews_count = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()

    def get_reviews_count(self, product):
        return product.reviews.count()

    def get_rating(self, product):
        average_rating = product.reviews.aggregate(Avg("rate"))["rate__avg"]
        return round(average_rating, 1) if average_rating else None

    class Meta:
        model = Product
        fields = "__all__"


class ProductSaleSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    salePrice = serializers.DecimalField(
        max_digits=10, decimal_places=2, source="salePrice.price"
    )
    dateFrom = serializers.DateField(source="salePrice.date_from")
    dateTo = serializers.DateField(source="salePrice.date_to")

    class Meta:
        model = Product
        fields = ["id", "price", "salePrice", "dateFrom", "dateTo", "title", "images"]


# class ReviewSerializer(ModelSerializer):
#     class Meta:
#         model = Review
#         fields = "__all__"


class SaleProductSerializer(ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ("id", "price", "salePrice", "dateFrom", "dateTo", "title", "images")


# class ProductSerializer(ModelSerializer):
#     #category = CategorySerializer(many=False, read_only=True)
#     tag = TagSerializer(many=False, read_only=True)
#     class Meta:
#         model = Product
#         fields = "__all__"
