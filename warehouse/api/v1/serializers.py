from rest_framework import serializers

from accounts.models import User
from marketplace.choices import MerchandiseStatus
from product.models import Product
from warehouse.models import DeliveryPoint, OrderingGoods, Warehouse


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = (
            "id",
            "full_address",
            "region",
            "confirm",
            "country",
            "opening_date",
            "closing_time",
            "status",
        )


class WarehouseCreateSerializer(serializers.ModelSerializer):
    full_address = serializers.CharField(required=True)
    region = serializers.CharField(required=True)
    country = serializers.CharField(required=True)

    class Meta:
        model = Warehouse
        fields = (
            "id",
            "full_address",
            "region",
            "confirm",
            "country",
            "opening_date",
            "closing_time",
            "status",
        )
        read_only_fields = ('id', 'confirm', 'status')


class DeliveryPointSerializer(serializers.ModelSerializer):
    delivery_warehouse = WarehouseSerializer()

    class Meta:
        model = DeliveryPoint
        fields = (
            "id",
            "delivery_warehouse",
            "full_address",
            "region",
            "confirm",
            "country",
            "opening_date",
            "closing_time",
            "status",
        )


class DeliveryPointCreateSerializer(serializers.ModelSerializer):
    full_address = serializers.CharField(required=True)
    region = serializers.CharField(required=True)
    country = serializers.CharField(required=True)

    class Meta:
        model = DeliveryPoint
        fields = (
            "delivery_warehouse",
            "full_address",
            "region",
            "confirm",
            "country",
            "opening_date",
            "closing_time",
            "status",
        )


class OrderingGoodsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderingGoods
        fields = (
            "id",
            "delivery_point",
            "product",
            "quantity",
            "status",
        )
        read_only_fields = ("id", "delivery_point", "product", "quantity")


class OrderingGoodsCreateSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        required=True, queryset=User.objects.all()
    )
    quantity = serializers.IntegerField(required=True)
    delivery_point = serializers.PrimaryKeyRelatedField(
        required=True, queryset=DeliveryPoint.objects.all()
    )
    product = serializers.PrimaryKeyRelatedField(
        required=True, queryset=Product.objects.all()
    )

    class Meta:
        model = OrderingGoods
        fields = (
            "user",
            "delivery_point",
            "product",
            "quantity",
            "status",
        )
        read_only_field = ("status",)

    @staticmethod
    def quantity_check(product, quantity):
        if quantity > product.amount:
            raise serializers.ValidationError({"error": "not_enough_product"})
        product.amount -= quantity
        if product.amount == 0:
            product.status = MerchandiseStatus.OUT_OF_STOCK
        product.save()

    def create(self, validated_data):
        self.quantity_check(
            product=validated_data.get("product"),
            quantity=validated_data.get("quantity"),
        )
        return super().create(validated_data)
