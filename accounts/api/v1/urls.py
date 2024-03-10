from django.urls import include, path

from accounts.api.v1.views import (
    RestorePasswordConfirmView,
    RestorePasswordView,
    SignInView,
    SignUpConfirmationCreateView,
    SignUpView,
    StaffMembersApiView,
    StaffMembersCreateApiView,
    StaffMembersRetrieveApiView,
    SupplierApiView,
    SupplierCreateApiView,
    SupplierRetrieveApiView,
)

urlpatterns = [
    path("sign-up/", SignUpView.as_view(), name="sign-up"),
    path(
        "sign-up-confirm/",
        SignUpConfirmationCreateView.as_view(),
        name="sms_confirmation",
    ),
    path("sign-in/", SignInView.as_view(), name="sign-in"),
    path("restore_password/", RestorePasswordView.as_view(), name="restore_password"),
    path(
        "user_recovery/<int:code>/",
        RestorePasswordConfirmView.as_view(),
        name="user_recovery",
    ),
    path(
        "supplier/",
        include(
            [
                path("list/", SupplierApiView.as_view(), name="supplier_list"),
                path(
                    "create/", SupplierCreateApiView.as_view(), name="supplier_create"
                ),
                path(
                    "<int:pk>/",
                    SupplierRetrieveApiView.as_view(),
                    name="supplier_retrieve",
                ),
            ]
        ),
    ),
    path(
        "staff-members/",
        include(
            [
                path("list/", StaffMembersApiView.as_view(), name="staff_members"),
                path(
                    "create/",
                    StaffMembersCreateApiView.as_view(),
                    name="staff_members_create",
                ),
                path(
                    "<int:pk>/",
                    StaffMembersRetrieveApiView.as_view(),
                    name="staff_members_retrieve",
                ),
            ]
        ),
    ),
]
