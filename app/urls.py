from django.contrib import admin
from django.urls import path
from .views import listProducts, productDetail, recommendedProducts


app_name = "products"

urlpatterns = [
    path('productsList/', listProducts, name="listProducts"),
    path('productsList/<id>/', productDetail, name="productDetail"),
    path('recommended/', recommendedProducts, name="recommendedProducts")
]
