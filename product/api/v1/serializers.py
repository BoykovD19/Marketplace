from rest_framework import serializers

from accounts.models import User
from product.models import Product, ProductPhoto, ProductReview
from warehouse.api.v1.serializers import DeliveryPointSerializer, WarehouseSerializer


class ProductSerializer(serializers.ModelSerializer):
    warehouse = WarehouseSerializer
    delivery_point = DeliveryPointSerializer
    country_of_production = serializers.CharField(required=False)

    class Meta:
        model = Product
        fields = (
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
        )


class ProductSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
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
        )
        read_only_field = ("supplier",)


class ProductReviewSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        required=True, queryset=User.objects.all()
    )

    class Meta:
        model = ProductReview
        fields = (
            "id",
            "user",
            "product",
            "grades",
            "review",
        )


class ProductPhotoSerializers(serializers.ModelSerializer):
    class Meta:
        model = ProductPhoto
        fields = (
            "id",
            "picture",
            "product",
        )
