from random import randrange

from django.db.models import Avg
from django.http import JsonResponse
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from django_filters.rest_framework.filters import OrderingFilter
from rest_framework.generics import ListCreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView


from .models import Product, Category, Tag
from .serializers import (
    ProductSerializer,
    CategorySerializer,
    TagSerializer,
    ProductSaleSerializer,
    ReviewSerializer,
)
from .paginator import CatalogPagination


class ProductList(generics.ListAPIView):
    serializer_class = ProductSerializer
    pagination_class = CatalogPagination

    def get_queryset(self):
        queryset = Product.objects.all()

        filter_name = self.request.query_params.get("filter[name]")
        if filter_name:
            queryset = queryset.filter(title__icontains=filter_name)

        filter_min_price = self.request.query_params.get("filter[minPrice]")
        if filter_min_price:
            queryset = queryset.filter(price__gte=filter_min_price)

        filter_max_price = self.request.query_params.get("filter[maxPrice]")
        if filter_max_price:
            queryset = queryset.filter(price__lte=filter_max_price)

        filter_free_delivery = self.request.query_params.get("filter[freeDelivery]")
        if filter_free_delivery:
            filter_free_delivery = filter_free_delivery.lower() == "true"
            queryset = queryset.filter(freeDelivery=filter_free_delivery)

        filter_available = self.request.query_params.get("filter[available]")
        if filter_available:
            filter_available = filter_available.lower() == "true"
            queryset = queryset.filter(count__gt=0, limited_edition=filter_available)

        sort = self.request.query_params.get("sort")
        if sort:
            sort_type = self.request.query_params.get("sortType", "asc")
            if sort == "reviews":
                queryset = queryset.annotate(avg_rating=Avg("reviews__rate")).order_by(
                    f"-avg_rating" if sort_type == "dec" else "avg_rating"
                )
            elif sort == "price":
                queryset = queryset.order_by(
                    f"-price" if sort_type == "dec" else "price"
                )

        return queryset


class CategoryList(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductLimited(APIView):
    def get(self, request):
        products = Product.objects.filter(limited_edition=True)[:16]
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PopularProductsView(APIView):
    def get(self, request):
        popular_products = Product.objects.order_by("-rating")[:10]
        serializer = ProductSerializer(popular_products, many=True)
        return Response(serializer.data)


class Banner(APIView):
    def get(self, request):
        popular_products = Product.objects.order_by("?")[:3]
        serializer = ProductSerializer(popular_products, many=True)
        return Response(serializer.data)


class ProductSalesView(generics.ListAPIView):
    serializer_class = ProductSaleSerializer
    queryset = Product.objects.filter(salePrice__isnull=False).only(
        "id",
        "price",
        "salePrice__price",
        "salePrice__date_from",
        "salePrice__date_to",
        "title",
    )
    pagination_class = CatalogPagination


# class ReviewList(generics.ListCreateAPIView):
#     queryset = Review.objects.all()
#     serializer_class = ReviewSerializer
class AddReviewView(APIView):
    def post(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        data = request.data
        data["product"] = product.id

        serializer = ReviewSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


# class ReviewDetail(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Review.objects.all()
#     serializer_class = ReviewSerializer


class TagsList(ListCreateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
