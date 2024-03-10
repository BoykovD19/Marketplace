from django.contrib import admin

from product.models import Product, ProductPhoto, ProductReview


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "warehouse",
        "delivery_point",
        "status",
        "cost",
        "amount",
        "article",
        "description",
        "country_of_production",
        "supplier",
    ]
    read_only_fields = ["article"]


@admin.register(ProductPhoto)
class ProductPhotoAdmin(admin.ModelAdmin):
    list_display = ["id", "product", "picture"]


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ["id", "product", "grades", "review"]
