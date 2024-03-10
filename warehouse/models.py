from django.core.validators import MinValueValidator
from django.db import models
from django_countries.fields import CountryField

from marketplace.choices import StorageStatus, SupplyStatus
from marketplace.models import CreatedUpdatedModel


class Warehouse(CreatedUpdatedModel):
    full_address = models.CharField(max_length=512)
    region = models.CharField(max_length=100)
    confirm = models.BooleanField(default=False)
    country = CountryField(null=True, blank=True)
    opening_date = models.DateTimeField(null=True, blank=True)
    closing_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        choices=StorageStatus.choices,
        default=StorageStatus.CLOSED,
        max_length=32,
    )

    class Meta:
        verbose_name = "warehouse"
        verbose_name_plural = "warehouse"

    def __str__(self):
        return f"{self.full_address}"


class DeliveryPoint(CreatedUpdatedModel):
    delivery_warehouse = models.ForeignKey(
        "warehouse.Warehouse", on_delete=models.PROTECT
    )
    full_address = models.CharField(max_length=512)
    region = models.CharField(max_length=100)
    confirm = models.BooleanField(default=False)
    country = CountryField(null=True, blank=True)
    opening_date = models.DateTimeField(blank=True, null=True)
    closing_time = models.DateTimeField(blank=True, null=True)
    status = models.CharField(
        choices=StorageStatus.choices,
        default=StorageStatus.CLOSED,
        max_length=32,
    )

    class Meta:
        verbose_name = "delivery_point"
        verbose_name_plural = "delivery_point"

    def __str__(self):
        return f"{self.full_address}"


class OrderingGoods(CreatedUpdatedModel):
    user = models.ForeignKey("accounts.User", on_delete=models.PROTECT, null=True)
    delivery_point = models.ForeignKey(
        "warehouse.DeliveryPoint", on_delete=models.PROTECT, null=True
    )
    product = models.ForeignKey("product.Product", on_delete=models.PROTECT)
    quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    status = models.CharField(
        choices=SupplyStatus.choices, default=SupplyStatus.ASSEMBLY_STAGE, max_length=32
    )

    def cancel(self):
        self.status = SupplyStatus.CANCELED
        self.product.amount += self.quantity
        self.product.save()
        self.save(update_fields=["status"])
