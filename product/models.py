from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django_countries.fields import CountryField

from marketplace.choices import MerchandiseStatus
from marketplace.models import CreatedUpdatedModel


class Product(CreatedUpdatedModel):
    name = models.CharField(max_length=512)
    warehouse = models.ForeignKey("warehouse.Warehouse", on_delete=models.PROTECT)
    delivery_point = models.ForeignKey(
        "warehouse.DeliveryPoint", on_delete=models.PROTECT, null=True
    )
    status = models.CharField(
        choices=MerchandiseStatus.choices,
        default=MerchandiseStatus.OUT_OF_STOCK,
        max_length=32,
    )
    cost = models.DecimalField(decimal_places=8, max_digits=20)
    amount = models.IntegerField(default=0)
    article = models.AutoField(primary_key=True, auto_created=True)
    description = models.TextField(default="")
    country_of_production = CountryField(null=True, blank=True, default="Ru")
    supplier = models.ForeignKey("accounts.Supplier", on_delete=models.PROTECT)

    class Meta:
        verbose_name = "product"
        verbose_name_plural = "products"

    def __str__(self):
        return self.name


class ProductPhoto(CreatedUpdatedModel):
    product = models.ForeignKey("product.Product", on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='product_photos/', max_length=200)

    class Meta:
        verbose_name = "product_photo"
        verbose_name_plural = "product_photos"

    def __str__(self):
        return f"{self.product.name} photo"


class ProductReview(CreatedUpdatedModel):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, null=True)
    product = models.ForeignKey("product.Product", on_delete=models.CASCADE)
    grades = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    review = models.CharField(max_length=1024, null=True, blank=True)

    class Meta:
        verbose_name = "product_reviews"
        verbose_name_plural = "product_reviews"

    def __str__(self):
        return f"{self.product.name} review"
