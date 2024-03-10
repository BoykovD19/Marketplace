import decimal
from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from accounts.models import StaffMembers, Supplier, User
from marketplace.choices import PositionsStatus, SupplyStatus
from product.models import Product
from warehouse.api.v1.serializers import (
    DeliveryPointCreateSerializer,
    DeliveryPointSerializer,
    OrderingGoodsSerializer,
    WarehouseSerializer,
)
from warehouse.models import DeliveryPoint, OrderingGoods, Warehouse


class AccountsTestCase(APITestCase):
    wr_list = reverse("wr_list")
    wr_create = reverse("wr_create")
    dp_list = reverse("dp_list")
    dp_create = reverse("dp_create")
    ordering_goods_create = reverse("ordering_goods_create")
    supply_ordering_list = reverse("supply_ordering_list")

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create(
            first_name="test", last_name="test2", email="test@gmauk.com", is_active=True
        )
        self.staff_members = StaffMembers.objects.create(
            user=self.user,
            salary=decimal.Decimal("0"),
            job_title=PositionsStatus.SUPER_USER,
        )
        self.warehouse = Warehouse.objects.create(
            full_address="test",
            region="tes3",
            country="Ru",
        )
        self.warehouse2 = Warehouse.objects.create(
            full_address="test1",
            region="tes31",
            country="Ru",
        )
        self.delivery_point = DeliveryPoint.objects.create(
            delivery_warehouse=self.warehouse,
            full_address="test",
            region="tes3",
            country="Ru",
        )
        self.supplier = Supplier.objects.create(
            user=self.user,
            company_name="roga i nos",
            taxpayer_identification_number="156296310345",
        )
        self.product = Product.objects.create(
            name="Планшет",
            warehouse=self.warehouse,
            cost=Decimal("123"),
            amount=400,
            supplier=self.supplier,
        )
        self.order_goods = OrderingGoods.objects.create(
            user=self.user,
            delivery_point=self.delivery_point,
            product=self.product,
            quantity=2,
            status=SupplyStatus.DELIVERED,
        )
        self.client.force_authenticate(self.user)

    def test_warehouse_list(self):
        response = self.client.get(self.wr_list)
        serializer = WarehouseSerializer(
            [self.warehouse, self.warehouse2], many=True
        ).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer)

    def test_warehouse_create(self):
        self.assertEqual(Warehouse.objects.count(), 2)
        response = self.client.post(
            self.wr_create,
            data={"full_address": "open", "region": "test", "country": "Ru"},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Warehouse.objects.count(), 3)

    def test_warehouse_negative(self):
        response = self.client.post(
            self.wr_create, data={"region": "test", "country": "Ru"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_warehouse_retrieve(self):
        response = self.client.get(reverse("wr_retrieve", args=(self.warehouse.id,)))
        serializer = WarehouseSerializer(self.warehouse).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer)

    def test_warehouse_retrieve_update(self):
        self.assertEqual(self.warehouse.full_address, "test")
        response = self.client.patch(
            reverse("wr_retrieve", args=(self.warehouse.id,)),
            data={"full_address": "open12"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.warehouse.refresh_from_db()
        self.assertEqual(self.warehouse.full_address, "open12")

    def test_warehouse_retrieve_delete(self):
        self.assertEqual(Warehouse.objects.count(), 2)
        response = self.client.delete(
            reverse("wr_retrieve", args=(self.warehouse2.id,))
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Warehouse.objects.count(), 1)

    def test_delivery_list(self):
        response = self.client.get(self.dp_list)
        serializer = DeliveryPointSerializer([self.delivery_point], many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer)

    def test_delivery_create(self):
        self.assertEqual(DeliveryPoint.objects.count(), 1)
        response = self.client.post(
            self.dp_create,
            data={
                "full_address": "open",
                "region": "test",
                "delivery_warehouse": self.warehouse.id,
                "country": "Ru",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DeliveryPoint.objects.count(), 2)

    def test_delivery_negative(self):
        response = self.client.post(
            self.dp_create, data={"region": "test", "country": "Ru"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delivery_retrieve(self):
        response = self.client.get(
            reverse("dp_retrieve", args=(self.delivery_point.id,))
        )
        serializer = DeliveryPointCreateSerializer(self.delivery_point).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer)

    def test_dilevery_point_update(self):
        self.assertEqual(self.warehouse.full_address, "test")
        response = self.client.patch(
            reverse("dp_retrieve", args=(self.delivery_point.id,)),
            data={"full_address": "open12"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.delivery_point.refresh_from_db()
        self.assertEqual(self.delivery_point.full_address, "open12")

    def test_ordering_goods_retrieve(self):
        response = self.client.get(reverse("og_retrieve", args=(self.order_goods.id,)))
        serializer = OrderingGoodsSerializer(self.order_goods).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer)

    def test_ordering_goods_delete(self):
        self.assertEqual(self.order_goods.status, SupplyStatus.DELIVERED)
        response = self.client.delete(reverse("og_cancel", args=(self.order_goods.id,)))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.order_goods.refresh_from_db()
        self.assertEqual(self.order_goods.status, SupplyStatus.CANCELED)

    def test_og_change_status(self):
        self.assertEqual(self.order_goods.status, SupplyStatus.DELIVERED)
        response = self.client.patch(
            reverse("og_change_status", args=(self.order_goods.id,)),
            data={"status": "en_route"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order_goods.refresh_from_db()
        self.assertEqual(self.order_goods.status, SupplyStatus.EN_ROUTE)

    def test_og_list(self):
        response = self.client.get(reverse("order_goods_list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = OrderingGoodsSerializer([self.order_goods], many=True).data
        self.assertEqual(response.data["results"], serializer)

    def test_og_history_list(self):
        response = self.client.get(reverse("ordering_goods_history"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = OrderingGoodsSerializer([self.order_goods], many=True).data
        self.assertEqual(response.data["results"], serializer)

    def test_og_create(self):
        self.assertEqual(OrderingGoods.objects.count(), 1)
        response = self.client.post(
            self.ordering_goods_create,
            data={
                "user": self.user.id,
                "delivery_point": self.delivery_point.id,
                "product": self.product.article,
                "quantity": 1,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(OrderingGoods.objects.count(), 2)

    def test_dp_ordering_goods_list(self):
        response = self.client.get(
            reverse("ordering_goods_dp", kwargs={"id": self.delivery_point.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = OrderingGoodsSerializer([self.order_goods], many=True).data
        self.assertEqual(response.data["results"], serializer)

    def test_supply_ordering_list(self):
        response = self.client.get(self.supply_ordering_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = OrderingGoodsSerializer([self.order_goods], many=True).data
        self.assertEqual(response.data["results"], serializer)
