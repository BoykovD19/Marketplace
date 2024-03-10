from rest_framework.fields import FileField

from marketplace import settings


class ViewMixin:
    @staticmethod
    def get_validated_data(serializer_cls, request):
        serializer = serializer_cls(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data


class PathFileField(FileField):
    def to_representation(self, value):
        if not value:
            return None
        return f"{settings.SCHEMA}{settings.HOST}{value.url}"
