from django.urls import include, path

from warehouse.api.v1.views import (
    DeliveryPointApiView,
    DeliveryPointCreateApiView,
    DeliveryPointRetrieveApiView,
    OrderingGoodsCanselApiView,
    OrderingGoodsCreate,
    OrderingGoodsHistory,
    OrderingGoodsListApiView,
    OrderingGoodsListWarehouseApiView,
    OrderingGoodsRetrieveApiView,
    OrderingGoodsStatusApiView,
    OrderingGoodsSupplyApiView,
    WarehouseApiView,
    WarehouseCreateApiView,
    WarehouseRetrieveApiView,
)

urlpatterns = [
    path("list/", WarehouseApiView.as_view(), name="wr_list"),
    path("create/", WarehouseCreateApiView.as_view(), name="wr_create"),
    path("<int:pk>/", WarehouseRetrieveApiView.as_view(), name="wr_retrieve"),
    path(
        "delivery-point/",
        include(
            [
                path("list/", DeliveryPointApiView.as_view(), name="dp_list"),
                path("create/", DeliveryPointCreateApiView.as_view(), name="dp_create"),
                path(
                    "<int:id>/",
                    include(
                        [
                            path(
                                "",
                                DeliveryPointRetrieveApiView.as_view(),
                                name="dp_retrieve",
                            ),
                            path(
                                "delivery-point/",
                                OrderingGoodsListWarehouseApiView.as_view(),
                                name="ordering_goods_dp",
                            ),
                        ]
                    ),
                ),
            ]
        ),
    ),
    path(
        "ordering-goods/<int:id>/",
        include(
            [
                path(
                    "retrieve/",
                    OrderingGoodsRetrieveApiView.as_view(),
                    name="og_retrieve",
                ),
                path("сancel/", OrderingGoodsCanselApiView.as_view(), name="og_cancel"),
                path(
                    "change-status/",
                    OrderingGoodsStatusApiView.as_view(),
                    name="og_change_status",
                ),
            ]
        ),
    ),
    path(
        "ordering-goods/",
        include(
            [
                path(
                    "list/", OrderingGoodsListApiView.as_view(), name="order_goods_list"
                ),
                path(
                    "ordering-goods-history/",
                    OrderingGoodsHistory.as_view(),
                    name="ordering_goods_history",
                ),
                path(
                    "create/",
                    OrderingGoodsCreate.as_view(),
                    name="ordering_goods_create",
                ),
                path(
                    "supply-list/",
                    OrderingGoodsSupplyApiView.as_view(),
                    name="supply_ordering_list",
                ),
            ]
        ),
    ),
]
