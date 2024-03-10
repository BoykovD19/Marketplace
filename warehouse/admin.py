from django.contrib import admin

from warehouse.models import DeliveryPoint, OrderingGoods, Warehouse


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "full_address",
        "region",
        "confirm",
        "country",
        "opening_date",
        "closing_time",
        "status",
    ]


@admin.register(DeliveryPoint)
class DeliveryPointAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "delivery_warehouse",
        "full_address",
        "region",
        "confirm",
        "country",
        "opening_date",
        "closing_time",
        "status",
    ]


@admin.register(OrderingGoods)
class OrderingGoodsAdmin(admin.ModelAdmin):
    list_display = ["id", "delivery_point", "product", "quantity", "status"]
