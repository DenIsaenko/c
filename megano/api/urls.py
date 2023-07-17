from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api import views
from shop.views import (
    CategoryList,
    ProductDetail,
    ProductList,
    TagsList,
    ProductLimited,
    ProductSalesView,
    AddReviewView,
    PopularProductsView,
    Banner,
)
from myauth.views import (
    SignInView,
    ProfileView,
    SignUpView,
    ChangePasswordView,
    ChangeAvatarView,
)
from card.views import CartDetailView, OrdersView, OrderDetailView, PaymentView

urlpatterns = [
    path("banners", Banner.as_view(), name="banner"),
    path("categories", CategoryList.as_view(), name="categories"),
    path("catalog", ProductList.as_view(), name="catalog"),
    path("products/popular", PopularProductsView.as_view(), name="product popular"),
    path("products/limited", ProductLimited.as_view(), name="product limited"),
    path("sales", ProductSalesView.as_view(), name="sales"),
    path("basket", CartDetailView.as_view(), name="basket"),
    path("orders", OrdersView.as_view()),
    path("sign-in", SignInView.as_view(), name="login"),
    path("sign-up", SignUpView.as_view(), name="register"),
    path("sign-out", views.signOut),
    path("product/<int:pk>", ProductDetail.as_view(), name="productDetail"),
    path("product/<int:pk>/reviews", AddReviewView.as_view(), name="add_review"),
    path("tags", TagsList.as_view(), name="tags"),
    path("profile", ProfileView.as_view(), name="profile"),
    path("profile/password", ChangePasswordView.as_view(), name="password"),
    path("profile/avatar", ChangeAvatarView.as_view(), name="avatar"),
    path("order/<int:id>", OrderDetailView.as_view()),
    path("payment/<int:id>", PaymentView.as_view(), name="payment"),
]
