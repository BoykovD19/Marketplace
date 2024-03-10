from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveAPIView,
    RetrieveDestroyAPIView,
    RetrieveUpdateDestroyAPIView,
    get_object_or_404,
)
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from accounts.permissions import IsActive, IsManager, IsSupplier
from marketplace import settings
from product.api.v1.filters import ProductFilter, ProductReviewFilter
from product.api.v1.serializers import (
    ProductPhotoSerializers,
    ProductReviewSerializer,
    ProductSerializer,
    ProductSerializerCreate,
)
from product.api.v1.utils import check_custom_permissions
from product.models import Product, ProductPhoto, ProductReview


class ProductApiView(ListAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.select_related("warehouse", "delivery_point", "supplier")
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProductFilter


class ProductCreateApiView(CreateAPIView):
    permission_classes = [IsSupplier]
    serializer_class = ProductSerializerCreate


class ProductRetrieveApiView(RetrieveAPIView):
    serializer_class = ProductSerializerCreate

    def get_object(self):
        return get_object_or_404(
            Product.objects.select_related("warehouse", "delivery_point", "supplier"),
            article=self.kwargs["article"],
        )


class ProductRetrieveUpdateApiView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsSupplier | IsManager]
    serializer_class = ProductSerializerCreate

    def get_object(self):
        return get_object_or_404(
            Product.objects.select_related("warehouse", "delivery_point", "supplier"),
            article=self.kwargs["article"],
        )

    def check_permissions(self, request, *args, **kwargs):
        instance = self.get_object()
        if not check_custom_permissions(user=request.user, article=instance.article):
            return None
        else:
            return instance

    def update(self, request, *args, **kwargs):
        instance = self.check_permissions(request=request)
        if not instance:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({})

    def delete(self, request, *args, **kwargs):
        instance = self.check_permissions(request=request)
        if not instance:
            return Response(status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductReviewApiView(ListAPIView):
    serializer_class = ProductReviewSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProductReviewFilter

    def get_queryset(self):
        return ProductReview.objects.select_related(
            "user",
            "product",
        ).filter(product__article=self.kwargs.get("article"))


class ProductReviewCreateApiView(CreateAPIView):
    permission_classes = [IsActive]
    serializer_class = ProductReviewSerializer


class ProductReviewRetrieveApiView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsManager]
    serializer_class = ProductReviewSerializer

    def get_object(self):
        return get_object_or_404(
            Product.objects.select_related("warehouse", "delivery_point", "supplier"),
            article=self.kwargs["article"],
        )


class ProductPhotoRetrieveApiView(ListAPIView):
    serializer_class = ProductPhotoSerializers

    def get_queryset(self):
        return ProductPhoto.objects.select_related("product").filter(
            product__article=self.kwargs["article"]
        )


class ProductPhotoCreateApiView(CreateAPIView):
    serializer_class = ProductPhotoSerializers
    parser_classes = (
        MultiPartParser,
        FormParser,
    )
    permission_classes = [IsSupplier]

    def post(self, request, *args, **kwargs):
        if not check_custom_permissions(
            user=request.user, article=request.data.get("product")
        ):
            return Response({"error": "you_do_not_have_access_to_this_item"})
        if (
            ProductPhoto.objects.filter(product=request.data.get("product")).count()
            > settings.NUMBER_OF_PRODUCT_PHOTOS
        ):
            return Response(
                {"error": "the_photo_limit_for_the_product_has_been_exceeded"}
            )
        return self.create(request, *args, **kwargs)


class ProductPhotoSupplyRetrieveApiView(RetrieveDestroyAPIView):
    serializer_class = ProductPhotoSerializers
    queryset = ProductPhoto.objects.all()
    permission_classes = [IsManager | IsSupplier]
    lookup_field = "article"

    def get_object(self):
        return get_object_or_404(
            Product.objects.select_related("warehouse", "delivery_point", "supplier"),
            article=self.kwargs["article"],
        )

    def check_permissions(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            Response({"error": "you_do_not_have_access_to_this_item"})
        if not check_custom_permissions(user=request.user, article=instance.article):
            Response({"error": "you_do_not_have_access_to_this_item"})
        else:
            return instance

    def delete(self, request, *args, **kwargs):
        instance = self.check_permissions(request=request)
        if not instance:
            return Response(status=status.HTTP_403_FORBIDDEN)
        try:
            photo_instance = ProductPhoto.objects.get(
                product_id=self.kwargs.get("article"), id=self.kwargs.get("id")
            )
            self.perform_destroy(photo_instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ProductPhoto.DoesNotExist:
            return Response({"error": "no_photo_found"}, status.HTTP_404_NOT_FOUND)
