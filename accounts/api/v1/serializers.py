from rest_framework import serializers

from accounts.api.v1.utils import generate_code
from accounts.models import EmailConfirmation, StaffMembers, Supplier, User
from marketplace import settings
from marketplace.choices import ConfirmationType, TypeEmailMessage
from marketplace.errors import SendException


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6, required=True, write_only=True)
    email = serializers.CharField(max_length=32, required=True)

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "password",
        )

    def validate(self, attrs):
        email = attrs.get("email").lower()
        password = attrs.get("password")
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {"error": "user_with_this_email_already_exist"}
            )
        if len(password) < settings.PASSWORD_LENGTH:
            raise serializers.ValidationError(
                f"minimum_password_length_{settings.PASSWORD_LENGTH}_characters"
            )
        if not any(char.isdigit() for char in password):
            raise serializers.ValidationError(
                "password_must_contain_at_least_one_number"
            )
        if password.isalpha() or password.isdigit():
            raise serializers.ValidationError(
                "password_cannot_consist_of_only_numbers_or_only_letters"
            )
        if not any(char.isupper() for char in password) or not any(
            char.islower() for char in password
        ):
            raise serializers.ValidationError(
                "password_must_contain_upper_and_lower_case_letters"
            )
        return attrs

    def create(self, validated_data):
        email = validated_data.get("email")
        if not EmailConfirmation.check_confirmation(email=email):
            raise serializers.ValidationError({"error": "email_not_confirmed"})
        password = validated_data.pop("password")
        validated_data["username"] = email
        user = super().create(validated_data)
        user.set_password(password)
        user.is_active = True
        user.save()
        return user


class EmailConfirmationCreateSerializer(serializers.Serializer):
    code = serializers.CharField(required=False)
    email = serializers.EmailField()

    def create(self, validated_data):
        instance = EmailConfirmation.objects.create(
            code=generate_code(),
            email=validated_data.get("email"),
            confirmation_type=ConfirmationType.SIGN_UP,
        )
        try:
            EmailConfirmation.create_confirmation(
                email=instance.email,
                data=instance.code,
                type_message=TypeEmailMessage.SUBMITTING_CODE,
            )
        except Exception:
            raise serializers.ValidationError({"error": "send_error"})
        return instance

    def update(self, instance, validated_data):
        instance.code = validated_data.get("code")
        instance.email = validated_data.get("email")
        instance.approve_confirmation()
        instance.save()
        return instance


class CredentialsSerializer(serializers.Serializer):
    email = serializers.CharField(
        write_only=True,
    )
    password = serializers.CharField(
        trim_whitespace=False,
        write_only=True,
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        try:
            user = User.objects.get(email=email)
            if not user.check_password(raw_password=password):
                raise ValueError("password not match")
        except (User.DoesNotExist, ValueError):
            raise serializers.ValidationError(
                {"error": "unable_to_log_in_with_provided_credentials"}
            )
        return attrs


class RestorePasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, allow_blank=False, allow_null=False)

    def validate(self, attrs):
        email = attrs.get("email")
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"error": "user_with_this_email_not_found."}
            )
        attrs["user"] = user
        return attrs

    def create(self, validated_data):
        user = validated_data["user"]
        try:
            instance = EmailConfirmation.objects.create(
                code=generate_code(),
                email=validated_data.get("email"),
                confirmation_type=ConfirmationType.RESTORE_PASSWORD,
            )

            EmailConfirmation.create_confirmation(
                email=user.email,
                data=instance.code,
                type_message=TypeEmailMessage.CHANGE_PASSWORD,
            )
        except SendException:
            raise serializers.ValidationError({"error": "email_confirmation_error"})
        return validated_data


class RestorePasswordConfirmSerializer(serializers.Serializer):
    password = serializers.CharField(required=True, write_only=True)
    password_confirmation = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        code = self.context["code"]
        if len(code) != settings.CODE_LENGTH:
            raise serializers.ValidationError({"error": "internal_error"})
        password = attrs.get("password")
        password_confirmation = attrs.get("password_confirmation")
        if password != password_confirmation:
            raise serializers.ValidationError({"error": "password_mismatch"})
        return attrs


class SupplierSerializers(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ("id", "user", "company_name", "taxpayer_identification_number")


class StaffMembersSerializers(serializers.ModelSerializer):
    class Meta:
        model = StaffMembers
        fields = (
            "id",
            "user",
            "warehouse",
            "delivery_point",
            "date_of_employment",
            "date_of_dismissal",
            "salary",
            "job_title",
        )

    def create(self, validated_data):
        user = validated_data.get("user")
        if StaffMembers.objects.filter(user=user).count() > 1:
            raise serializers.ValidationError(
                {"error": "the_user_already_has_a_position"}
            )
        user = super().create(validated_data)
        return user
