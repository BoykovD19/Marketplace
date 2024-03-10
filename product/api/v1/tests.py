import decimal
from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from accounts.models import StaffMembers, Supplier, User
from marketplace.choices import PositionsStatus
from product.api.v1.serializers import ProductReviewSerializer, ProductSerializer
from product.models import Product, ProductPhoto, ProductReview
from warehouse.models import Warehouse


class ProductTestCase(APITestCase):
    product_list = reverse("product_list")
    product_create = reverse("product_create")
    review_create = reverse("review_create")
    product_photo_create = reverse("product_photo_create")

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
        self.client.force_authenticate(self.user)
        self.supplier = Supplier.objects.create(
            user=self.user,
            company_name="Roga i copita",
            taxpayer_identification_number="12543124512",
        )
        self.product = Product.objects.create(
            name="Носки Шерстяные",
            warehouse=self.warehouse,
            cost=Decimal("20"),
            supplier=self.supplier,
        )
        self.product1 = Product.objects.create(
            name="Пояс из шерсти собаки",
            warehouse=self.warehouse,
            cost=Decimal("150"),
            supplier=self.supplier,
        )
        self.photo = ProductPhoto.objects.create(
            product=self.product, picture="test/fewefwefwef"
        )
        self.review = ProductReview.objects.create(
            user=self.user,
            product=self.product,
            grades=4,
        )

    def test_product_list(self):
        response = self.client.get(self.product_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = ProductSerializer([self.product, self.product1], many=True).data
        self.assertEqual(response.data["results"], serializer)

    def test_product_create(self):
        self.assertEqual(Product.objects.count(), 2)
        response = self.client.post(
            self.product_create,
            data={
                "name": "Швабра",
                "warehouse": self.warehouse.id,
                "cost": Decimal("123"),
                "supplier": self.supplier.id,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 3)

    def test_product_retrieve(self):
        response = self.client.get(
            reverse("product_retrieve", kwargs={"article": self.product1.article})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = ProductSerializer(self.product1).data
        self.assertEqual(response.data, serializer)

    def test_product_retrieve_update(self):
        self.assertEqual(self.product1.cost, Decimal("150"))
        response = self.client.patch(
            reverse("product_update", kwargs={"article": self.product1.article}),
            data={
                "cost": Decimal("200"),
                "name": "Valun",
                "warehouse": self.warehouse.id,
                "supplier": self.supplier.id,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product1.refresh_from_db()
        self.assertEqual(self.product1.cost, Decimal("200"))

    def test_product_update_retrieve(self):
        response = self.client.get(
            reverse("product_update", kwargs={"article": self.product1.article}),
            data={
                "cost": Decimal("150"),
                "name": "Valun",
                "warehouse": self.warehouse.id,
                "supplier": self.supplier.id,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product1.refresh_from_db()
        self.assertEqual(self.product1.cost, Decimal("150"))

    def test_product_photo_delete(self):
        self.assertEqual(ProductPhoto.objects.count(), 1)
        response = self.client.delete(
            reverse(
                "product_photo_delete",
                kwargs={"article": self.product.article, "id": self.photo.id},
            )
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ProductPhoto.objects.count(), 0)

    def test_review_create(self):
        self.assertEqual(ProductReview.objects.count(), 1)
        response = self.client.post(
            self.review_create,
            data={"user": self.user.id, "product": self.product.article, "grades": 5},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductReview.objects.count(), 2)

    def test_review_list(self):
        response = self.client.get(
            reverse("review_list", kwargs={"article": self.product.article})
        )
        serializer = ProductReviewSerializer([self.review], many=True).data
        self.assertEqual(response.data["results"], serializer)
