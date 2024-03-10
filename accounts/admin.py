from django.contrib import admin
from rest_framework.authtoken.models import Token

from accounts.models import EmailConfirmation, StaffMembers, Supplier, User


@admin.register(User)
class User(admin.ModelAdmin):
    list_display = [
        "id",
        "first_name",
        "last_name",
        "username",
        "email",
        "activation_key",
        "email_2fa",
        "temporary_email",
        "is_active",
        "created_at",
    ]


@admin.register(EmailConfirmation)
class EmailConfirmation(admin.ModelAdmin):
    list_display = ["email", "code", "confirm"]


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ["user", "company_name", "taxpayer_identification_number"]


@admin.register(StaffMembers)
class StaffMembersAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "warehouse",
        "delivery_point",
        "date_of_employment",
        "date_of_dismissal",
        "salary",
        "job_title",
    ]


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ["key", "user", "created"]
