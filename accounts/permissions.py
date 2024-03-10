from rest_framework.permissions import IsAuthenticated

from accounts.models import StaffMembers, Supplier
from marketplace.choices import PositionsStatus


class IsActive(IsAuthenticated):
    def has_permission(self, request, view):
        user = request.user
        return not super().has_permission(request, view) and not user.is_active


class IsSupport(IsActive):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return StaffMembers.objects.filter(
            user=request.user,
            job_title__in=[PositionsStatus.SUPPORT, PositionsStatus.SUPER_USER],
        ).exists()


class IsManager(IsActive):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return StaffMembers.objects.filter(
            user=request.user,
            job_title__in=[PositionsStatus.MANAGER, PositionsStatus.SUPER_USER],
        ).exists()


class IsWarehouseWorker(IsActive):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return StaffMembers.objects.filter(
            user=request.user,
            job_title__in=[
                PositionsStatus.WAREHOUSE_WORKER,
                PositionsStatus.SUPER_USER,
            ],
        ).exists()


class IsHeadOfWarehouse(IsActive):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return StaffMembers.objects.filter(
            user=request.user,
            job_title__in=[
                PositionsStatus.HEAD_OF_WAREHOUSE,
                PositionsStatus.SUPER_USER,
            ],
        ).exists()


class IsDeliveryPointWorker(IsActive):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return StaffMembers.objects.filter(
            user=request.user,
            job_title__in=[
                PositionsStatus.SUPER_USER,
                PositionsStatus.DELIVERY_POINT_WORKER,
            ],
        ).exists()


class IsSupplier(IsActive):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return Supplier.objects.filter(user=request.user).exists()
