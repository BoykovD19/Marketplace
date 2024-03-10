from unittest import mock

from _decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from accounts.api.v1.serializers import StaffMembersSerializers, SupplierSerializers
from accounts.models import (
    EmailConfirmation,
    LoginHistory,
    StaffMembers,
    Supplier,
    User,
)
from marketplace.choices import ConfirmationType, PositionsStatus


class AccountsTestCase(APITestCase):
    sign_up = reverse("sign-up")
    sms_confirmation = reverse("sms_confirmation")
    sign_in = reverse("sign-in")
    restore_password = reverse("restore_password")
    supplier_list = reverse("supplier_list")
    supplier_create = reverse("supplier_create")
    staff_members = reverse("staff_members")
    staff_members_create = reverse("staff_members_create")

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create(
            first_name="test",
            last_name="tes3",
            email="testemail@gmail.com",
            is_active=True,
            password="qwe123qwe",
        )
        self.client.force_authenticate(self.user)
        self.confirmation = EmailConfirmation.objects.create(
            email="testemail1@gmail.com",
            code="2321",
            confirm=False,
            confirmation_type=ConfirmationType.SIGN_IN,
        )
        self.confirmation2 = EmailConfirmation.objects.create(
            email="testemail1@gmail.com",
            code="23221",
            confirm=True,
            confirmation_type=ConfirmationType.SIGN_UP,
        )
        self.confirmation3 = EmailConfirmation.objects.create(
            email="testemail@gmail.com",
            code="232212",
            confirm=True,
            confirmation_type=ConfirmationType.RESTORE_PASSWORD,
        )
        self.supplier1 = Supplier.objects.create(
            user=self.user,
            company_name="Roga i copita",
            taxpayer_identification_number="12543124512",
        )
        self.supplier2 = Supplier.objects.create(
            user=self.user,
            company_name="2 tyza",
            taxpayer_identification_number="11543124512",
        )
        self.staff_members_user = StaffMembers.objects.create(
            user=self.user,
            salary=Decimal("124000"),
            job_title=PositionsStatus.SUPER_USER,
        )
        self.confirmation = EmailConfirmation.objects.create(
            email="testzarb12@gmail.com",
            code="2321",
            confirm=True,
            confirmation_type=ConfirmationType.SIGN_UP,
        )

    def test_user_sign_up(self):
        self.assertEqual(User.objects.count(), 1)
        response = self.client.post(
            self.sign_up,
            data={"email": "testemail1@gmail.com", "password": "Qwe123qwe"},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

    def test_user_sign_up_negative(self):
        self.assertEqual(User.objects.count(), 1)
        response = self.client.post(self.sign_up)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)

    def test_user_sms_confirmation(self):
        with mock.patch("accounts.models.EmailConfirmation.create_confirmation"):
            self.assertEqual(EmailConfirmation.objects.count(), 4)
            response = self.client.post(
                self.sms_confirmation, data={"email": "lordyourmam@gmail.com"}
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(EmailConfirmation.objects.count(), 5)

    def test_sign_in_confirmation(self):
        response = self.client.patch(self.sign_in, data={"code": "232212"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_sign_in_confirmation_login_history(self):
        self.assertEqual(LoginHistory.objects.count(), 0)
        response = self.client.patch(self.sign_in, data={"code": "232212"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(LoginHistory.objects.count(), 1)

    def test_sign_in(self):
        with mock.patch("accounts.models.EmailConfirmation.create_confirmation"):
            self.assertEqual(User.objects.count(), 1)
            self.client.post(
                self.sign_up,
                data={"email": "testzarb12@gmail.com", "password": "Wwe123qwe1"},
            )
            self.assertEqual(User.objects.count(), 2)
            self.assertEqual(EmailConfirmation.objects.count(), 4)
            response = self.client.post(
                self.sign_in,
                data={"email": "testzarb12@gmail.com", "password": "Wwe123qwe1"},
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(EmailConfirmation.objects.count(), 4)

    def test_sign_in_confirm(self):
        with mock.patch("accounts.models.EmailConfirmation.create_confirmation"):
            self.assertEqual(User.objects.count(), 1)
            self.client.post(
                self.sign_up,
                data={"email": "testemail1@gmail.com", "password": "Qwe123qwe1"},
            )
            self.assertEqual(EmailConfirmation.objects.count(), 4)
            user = User.objects.get(email="testemail1@gmail.com")
            user.email_2fa = True
            user.save()
            user.refresh_from_db()
            self.assertEqual(User.objects.count(), 2)
            response = self.client.post(
                self.sign_in,
                data={"email": "testemail1@gmail.com", "password": "Qwe123qwe1"},
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(EmailConfirmation.objects.count(), 5)

    def test_restore_password(self):
        with mock.patch("accounts.models.EmailConfirmation.create_confirmation"):
            self.assertEqual(EmailConfirmation.objects.count(), 4)
            response = self.client.post(
                self.restore_password, data={"email": "testemail@gmail.com"}
            )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(EmailConfirmation.objects.count(), 5)

    def test_restore_password_negative(self):
        with mock.patch("accounts.models.EmailConfirmation.create_confirmation"):
            self.assertEqual(EmailConfirmation.objects.count(), 4)
            response = self.client.post(
                self.restore_password, data={"email": "testemail12312@gmail.com"}
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(EmailConfirmation.objects.count(), 4)

    def test_user_recovery(self):
        with mock.patch("accounts.models.EmailConfirmation.create_confirmation"):
            response = self.client.patch(
                reverse("user_recovery", kwargs={"code": self.confirmation3.code}),
                data={"password": "Test123", "password_confirmation": "Test123"},
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.user.refresh_from_db()
            response = self.client.post(
                self.sign_in,
                data={"email": self.confirmation3.email, "password": "Test123"},
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_supplier_list(self):
        response = self.client.get(self.supplier_list)
        serializer = SupplierSerializers(
            [self.supplier1, self.supplier2], many=True
        ).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer)

    def test_supplier_create(self):
        self.assertEqual(Supplier.objects.count(), 2)
        response = self.client.post(
            self.supplier_create,
            data={"user": self.user.id, "company_name": "roga i roga"},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Supplier.objects.count(), 3)

    def test_supplier_negative(self):
        response = self.client.post(self.supplier_create, data={"user": self.user.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_supplier(self):
        response = self.client.get(
            reverse("supplier_retrieve", args=(self.supplier1.id,))
        )
        serializer = SupplierSerializers(self.supplier1).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer)

    def test_retrieve_supplier_path(self):
        self.assertEqual(self.supplier1.company_name, "Roga i copita")
        response = self.client.patch(
            reverse("supplier_retrieve", args=(self.supplier1.id,)),
            data={"company_name": "roga i noga"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.supplier1.refresh_from_db()
        self.assertEqual(self.supplier1.company_name, "roga i noga")

    def test_retrieve_supplier_delete(self):
        self.assertEqual(Supplier.objects.count(), 2)
        response = self.client.delete(
            reverse("supplier_retrieve", args=(self.supplier1.id,))
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Supplier.objects.count(), 1)

    def test_staff_member_list(self):
        response = self.client.get(self.staff_members)
        serializer = StaffMembersSerializers([self.staff_members_user], many=True).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer)

    def test_staff_members_create(self):
        self.assertEqual(StaffMembers.objects.count(), 1)
        response = self.client.post(
            self.staff_members_create,
            data={
                "user": self.user.id,
                "salary": Decimal("124"),
                "job_title": PositionsStatus.SUPPORT,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(StaffMembers.objects.count(), 2)

    def test_staff_members_retrieve(self):
        response = self.client.get(
            reverse("staff_members_retrieve", args=(self.staff_members_user.id,))
        )
        serializer = StaffMembersSerializers(self.staff_members_user).data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer)

    def test_staff_members_update(self):
        self.assertEqual(self.staff_members_user.job_title, PositionsStatus.SUPER_USER)
        response = self.client.patch(
            reverse("staff_members_retrieve", args=(self.staff_members_user.id,)),
            data={
                "user": self.user.id,
                "salary": Decimal("214"),
                "job_title": PositionsStatus.MANAGER,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.staff_members_user.refresh_from_db()
        self.assertEqual(self.staff_members_user.job_title, PositionsStatus.MANAGER)

    def test_staff_members_delete(self):
        self.assertEqual(StaffMembers.objects.count(), 1)
        response = self.client.delete(
            reverse("staff_members_retrieve", args=(self.staff_members_user.id,))
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(StaffMembers.objects.count(), 0)
