from django.db import models


class ConfirmationType(models.TextChoices):
    SIGN_IN = "sign_in"
    SIGN_UP = "sign_up"
    RESTORE_PASSWORD = "restore_password"


class TypeEmailMessage(models.TextChoices):
    SUBMITTING_CODE = "submitting_code"
    CHANGE_PASSWORD = "change_password"


class Role(models.TextChoices):
    USER = "user"
    SUPPORT = "support"
    ADMIN = "admin"


class StorageStatus(models.TextChoices):
    OPEN = "open"
    CLOSED = "closed"
    PREPARE_FOR_THE_OPENING = "prepare for the opening"
    PREPARE_TO_CLOSE = "prepare_to_close"


class PositionsStatus(models.TextChoices):
    SUPPORT = "support"
    MANAGER = "manager"
    WAREHOUSE_WORKER = "warehouse_worker"
    HEAD_OF_WAREHOUSE = "head_of_warehouse"
    DELIVERY_POINT_WORKER = "delivery_point_worker"
    SUPER_USER = "superuser"


class MerchandiseStatus(models.TextChoices):
    ON_SALE = "on_sale"
    OUT_OF_STOCK = "out_of_stock"


class SupplyStatus(models.TextChoices):
    ASSEMBLY_STAGE = "assembly_stage"
    EN_ROUTE = "en_route"
    DELIVERED = "delivered"
    CANCELED = "сanceled"


class OrderStatus(models.TextChoices):
    ASSEMBLY_STAGE = "assembly_stage"
    EN_ROUTE = "en_route"
    DELIVERED = "delivered"
    Canceled = "сanceled"
