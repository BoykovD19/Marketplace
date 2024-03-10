from rest_framework import status
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
    UpdateAPIView,
    get_object_or_404,
)
from rest_framework.response import Response

from accounts.permissions import (
    IsActive,
    IsDeliveryPointWorker,
    IsHeadOfWarehouse,
    IsManager,
    IsSupplier,
    IsWarehouseWorker,
)
from marketplace.choices import SupplyStatus
from warehouse.api.v1.serializers import (
    DeliveryPointCreateSerializer,
    DeliveryPointSerializer,
    OrderingGoodsCreateSerializer,
    OrderingGoodsSerializer,
    WarehouseCreateSerializer,
    WarehouseSerializer,
)
from warehouse.models import DeliveryPoint, OrderingGoods, Warehouse


class WarehouseApiView(ListAPIView):
    permission_classes = [IsHeadOfWarehouse, IsWarehouseWorker]
    serializer_class = WarehouseSerializer
    queryset = Warehouse.objects.all()


class WarehouseCreateApiView(CreateAPIView):
    permission_classes = [IsManager]
    serializer_class = WarehouseCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({}, status=status.HTTP_201_CREATED)


class WarehouseRetrieveApiView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsHeadOfWarehouse]
    serializer_class = WarehouseCreateSerializer
    queryset = Warehouse.objects.all()


class DeliveryPointApiView(ListAPIView):
    permission_classes = [IsDeliveryPointWorker]
    serializer_class = DeliveryPointSerializer
    queryset = DeliveryPoint.objects.select_related("delivery_warehouse")


class DeliveryPointCreateApiView(CreateAPIView):
    permission_classes = [IsActive]
    serializer_class = DeliveryPointCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({}, status=status.HTTP_201_CREATED)


class DeliveryPointRetrieveApiView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsDeliveryPointWorker]
    serializer_class = DeliveryPointCreateSerializer
    queryset = DeliveryPoint.objects.select_related("delivery_warehouse")
    lookup_field = "id"


class OrderingGoodsListApiView(ListAPIView):
    permission_classes = [IsManager]
    serializer_class = OrderingGoodsSerializer
    queryset = OrderingGoods.objects.select_related(
        "user", "delivery_point", "product"
    ).order_by("-created_at")


class OrderingGoodsHistory(ListAPIView):
    permission_classes = [IsActive]
    serializer_class = OrderingGoodsSerializer

    def get_queryset(self):
        return OrderingGoods.objects.select_related(
            "user", "delivery_point", "product"
        ).filter(user=self.request.user, status=SupplyStatus.DELIVERED)


class OrderingGoodsRetrieveApiView(RetrieveAPIView):
    permission_classes = [IsActive]
    serializer_class = OrderingGoodsSerializer

    def get_object(self):
        return get_object_or_404(
            OrderingGoods.objects.select_related("user", "delivery_point", "product"),
            id=self.kwargs["id"],
        )


class OrderingGoodsCanselApiView(OrderingGoodsRetrieveApiView, DestroyAPIView):
    permission_classes = [IsActive | IsDeliveryPointWorker]

    def perform_destroy(self, instance):
        instance = self.get_object()
        if instance.status == SupplyStatus.EN_ROUTE:
            return Response(
                {"error": ["the_order_cannot_be_cancelled_at_this_stage"]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        instance.cancel()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderingGoodsStatusApiView(OrderingGoodsRetrieveApiView, UpdateAPIView):
    permission_classes = [IsManager | IsWarehouseWorker | IsDeliveryPointWorker]


class OrderingGoodsListWarehouseApiView(ListAPIView):
    permission_classes = [IsDeliveryPointWorker]
    serializer_class = OrderingGoodsSerializer

    def get_queryset(self):
        return OrderingGoods.objects.select_related(
            "user", "delivery_point", "product"
        ).filter(delivery_point_id=self.kwargs.get("id"))


class OrderingGoodsSupplyApiView(ListAPIView):
    permission_classes = [IsSupplier]
    serializer_class = OrderingGoodsSerializer

    def get_queryset(self):
        return OrderingGoods.objects.select_related(
            "user", "delivery_point", "product"
        ).filter(product__supplier__user=self.request.user)


class OrderingGoodsCreate(CreateAPIView):
    permission_classes = [IsActive]
    serializer_class = OrderingGoodsCreateSerializer
