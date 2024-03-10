from uuid import uuid4

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from accounts.managers import LoginHistoryManager, UserManager
from accounts.tasks import send_simple_code
from marketplace.choices import ConfirmationType, PositionsStatus, Role
from marketplace.errors import SendException
from marketplace.models import CreatedUpdatedModel


class User(AbstractBaseUser, PermissionsMixin):
    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]
    Role = Role
    username = models.CharField(max_length=60, default="", blank=True, unique=True)
    first_name = models.CharField(max_length=150, default="", blank=False)
    last_name = models.CharField(max_length=150, default="", blank=False)
    email = models.EmailField(
        null=False,
        blank=False,
        unique=True,
        db_index=True,
    )
    activation_key = models.UUIDField(
        default=uuid4,
        blank=False,
        null=False,
        unique=True,
    )
    email_2fa = models.BooleanField(default=False)
    temporary_email = models.CharField(max_length=50, default="", blank=True)
    is_active = models.BooleanField(
        default=False,
        help_text="Designates whether this user should be treated as active."
        "Unselect this instead of deleting accounts.",
    )
    role = models.CharField(max_length=30, choices=Role.choices, default=Role.USER)
    is_staff = models.BooleanField(
        default=False,
        help_text="Designates whether the user can log into this admin site.",
    )
    created_at = models.DateTimeField(auto_now_add=True, null=False)

    objects = UserManager()

    def update_password(self, password):
        self.set_password(password)
        self.save()

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"


class EmailConfirmation(CreatedUpdatedModel):
    email = models.EmailField()
    code = models.CharField(max_length=10)
    confirm = models.BooleanField(default=False)
    confirmation_type = models.CharField(
        choices=ConfirmationType.choices,
        default=ConfirmationType.SIGN_IN,
        max_length=32,
    )

    @classmethod
    def check_confirmation(cls, email: str):
        try:
            cls.objects.get(email=email, confirm=True)
            return True
        except cls.DoesNotExist:
            return False

    @classmethod
    def create_confirmation(cls, email: str, data: str, type_message: str):
        try:
            send_simple_code.s().delay(to=email, data=data, type_message=type_message)
        except Exception:
            raise SendException

    def approve_confirmation(self):
        self.confirm = True
        self.save(update_fields=["confirm"])


class LoginHistory(CreatedUpdatedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    agent = models.CharField(max_length=256, null=True)
    ip = models.GenericIPAddressField()

    objects = LoginHistoryManager()

    class Meta:
        verbose_name = "LoginHistory"
        verbose_name_plural = "LoginHistory"

    @classmethod
    def already_logged(cls, user):
        return LoginHistory.objects.filter(user=user).exists()


class Supplier(CreatedUpdatedModel):
    user = models.ForeignKey("accounts.User", on_delete=models.PROTECT)
    company_name = models.CharField(max_length=256)
    taxpayer_identification_number = models.CharField(
        max_length=12, unique=True, null=True
    )


class StaffMembers(CreatedUpdatedModel):
    user = models.ForeignKey("accounts.User", on_delete=models.PROTECT)
    warehouse = models.ForeignKey(
        "warehouse.Warehouse", on_delete=models.PROTECT, null=True, blank=True
    )
    delivery_point = models.ForeignKey(
        "warehouse.DeliveryPoint", on_delete=models.PROTECT, null=True, blank=True
    )
    date_of_employment = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    date_of_dismissal = models.DateTimeField(null=True, blank=True)
    salary = models.DecimalField(decimal_places=8, max_digits=20)
    job_title = models.CharField(
        choices=PositionsStatus.choices, default=PositionsStatus.SUPPORT, max_length=256
    )
