from accounts.models import StaffMembers
from marketplace.choices import PositionsStatus
from product.models import Product


def check_custom_permissions(user, article):
    product = Product.objects.select_related(
        "warehouse", "delivery_point", "supplier"
    ).filter(supplier__user__email=user, article=article)
    user = StaffMembers.objects.get(user__email=user.email)
    if product or user.job_title == PositionsStatus.MANAGER:
        return True
