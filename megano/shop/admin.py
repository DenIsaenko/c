from django.contrib import admin

from .models import (
    Category,
    Product,
    Tag,
    SalePrice,
    Subcategory,
    ProductImage,
    Review,
    Specification,
)

admin.site.register(Category)

admin.site.register(Product)
admin.site.register(Tag)
admin.site.register(ProductImage)
admin.site.register(Subcategory)
admin.site.register(Review)
admin.site.register(Specification)
admin.site.register(SalePrice)
