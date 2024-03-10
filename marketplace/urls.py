from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/accounts/", include("accounts.api.v1.urls")),
    path("api/v1/warehouse/", include("warehouse.api.v1.urls")),
    path("api/v1/product/", include("product.api.v1.urls")),
]
