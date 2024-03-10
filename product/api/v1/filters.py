from django_filters import filters
from django_filters.filterset import FilterSet

from product.models import Product, ProductReview


class ProductFilter(FilterSet):
    name = filters.CharFilter(field_name="name")
    cost = filters.NumberFilter(field_name="cost")
    amount = filters.NumberFilter(field_name="amount")

    class Meta:
        model = Product
        fields = ["name", "cost", "amount"]


class ProductReviewFilter(FilterSet):
    class Meta:
        model = ProductReview
        fields = []

    o = filters.OrderingFilter(
        fields=(("grades", "grades"),),
    )
