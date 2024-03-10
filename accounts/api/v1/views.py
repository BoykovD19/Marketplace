from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
    UpdateAPIView,
    get_object_or_404,
)
from rest_framework.response import Response

from accounts.api.v1.serializers import (
    CredentialsSerializer,
    EmailConfirmationCreateSerializer,
    RestorePasswordConfirmSerializer,
    RestorePasswordSerializer,
    SignUpSerializer,
    StaffMembersSerializers,
    SupplierSerializers,
)
from accounts.api.v1.utils import generate_code
from accounts.models import (
    EmailConfirmation,
    LoginHistory,
    StaffMembers,
    Supplier,
    User,
)
from accounts.permissions import IsHeadOfWarehouse, IsManager
from marketplace.choices import TypeEmailMessage
from marketplace.errors import SendException


class SignUpView(CreateAPIView):
    serializer_class = SignUpSerializer


class SignUpConfirmationCreateView(CreateAPIView, UpdateAPIView):
    serializer_class = EmailConfirmationCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        instance = get_object_or_404(
            EmailConfirmation.objects.filter(
                email=serializer.data.get("email"), code=serializer.data.get("code")
            )
        )
        instance.approve_confirmation()
        return Response({})


class SignInView(CreateAPIView, UpdateAPIView):
    serializer_class = CredentialsSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(email=request.data.get("email"))
        if not user.email_2fa:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        else:
            try:
                code = generate_code()
                confirmation = EmailConfirmation.objects.create(
                    code=code, email=user.email
                )
                confirmation.create_confirmation(
                    email=user.email,
                    data=code,
                    type_message=TypeEmailMessage.SUBMITTING_CODE,
                )
            except SendException:
                return Response({"error": "email_confirmation_error"})
            return Response({}, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        code = self.request.data.get("code")
        try:
            confirmation = EmailConfirmation.objects.get(code=code)
            user = User.objects.get(email=confirmation.email)
            if not user.is_active:
                return Response(
                    {"error": "user_is_not_active"}, status.HTTP_400_BAD_REQUEST
                )
            token, _ = Token.objects.get_or_create(user=user)
            LoginHistory.objects.create_history(request=request, user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        except EmailConfirmation.DoesNotExist:
            return Response({"error": "code_is_not_valid"}, status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "user_is_not_found"}, status.HTTP_400_BAD_REQUEST)


class RestorePasswordView(CreateAPIView):
    serializer_class = RestorePasswordSerializer


class RestorePasswordConfirmView(UpdateAPIView):
    serializer_class = RestorePasswordConfirmSerializer

    def get_object(self):
        return EmailConfirmation.objects.get(code=self.kwargs["code"])

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = RestorePasswordConfirmSerializer(
            data=request.data, context={"code": instance.code}
        )
        serializer.is_valid(raise_exception=True)
        User.objects.get(email=instance.email).update_password(request.data["password"])
        return Response({})


class SupplierApiView(ListAPIView):
    permission_classes = [IsManager]
    serializer_class = SupplierSerializers
    queryset = Supplier.objects.select_related("user")


class SupplierCreateApiView(CreateAPIView):
    permission_classes = [IsManager]
    serializer_class = SupplierSerializers


class SupplierRetrieveApiView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsManager | IsHeadOfWarehouse]
    serializer_class = SupplierSerializers
    queryset = Supplier.objects.select_related("user")


class StaffMembersApiView(ListAPIView):
    permission_classes = [IsManager]
    serializer_class = StaffMembersSerializers
    queryset = StaffMembers.objects.select_related(
        "user", "warehouse", "delivery_point"
    )


class StaffMembersCreateApiView(CreateAPIView):
    permission_classes = [IsManager]
    serializer_class = StaffMembersSerializers


class StaffMembersRetrieveApiView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsManager | IsHeadOfWarehouse]
    serializer_class = StaffMembersSerializers
    queryset = StaffMembers.objects.select_related(
        "user", "warehouse", "delivery_point"
    )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({})
