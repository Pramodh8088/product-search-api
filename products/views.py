from decimal import Decimal, InvalidOperation

from django.db.models import Q, Count, Sum, Avg

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from .models import Product
from .serializers import ProductSerializer


class ProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    ordering = ["id"]

    def get_queryset(self):
        queryset = Product.objects.all()

        search = self.request.query_params.get("search")

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(description__icontains=search)
            )

        category = self.request.query_params.get("category")

        if category:
            queryset = queryset.filter(
                category__iexact=category
            )

        min_price = self.request.query_params.get("min_price")
        min_value = None

        if min_price is not None:
            try:
                min_value = Decimal(min_price)

                if not min_value.is_finite() or min_value < 0:
                    raise InvalidOperation

            except (InvalidOperation, ValueError):
                raise ValidationError({
                    "min_price": "Enter a valid non-negative price."
                })

            queryset = queryset.filter(
                price__gte=min_value
            )

        max_price = self.request.query_params.get("max_price")
        max_value = None

        if max_price is not None:
            try:
                max_value = Decimal(max_price)

                if not max_value.is_finite() or max_value < 0:
                    raise InvalidOperation

            except (InvalidOperation, ValueError):
                raise ValidationError({
                    "max_price": "Enter a valid non-negative price."
                })

            queryset = queryset.filter(
                price__lte=max_value
            )

        if (
            min_value is not None
            and max_value is not None
            and min_value > max_value
        ):
            raise ValidationError({
                "price": "min_price cannot exceed max_price."
            })

        return queryset


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]


class ProductSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        summary = Product.objects.aggregate(
            total_products=Count("id"),
            total_stock=Sum("stock"),
            average_price=Avg("price")
        )

        average_price = summary["average_price"]

        return Response({
            "total_products": summary["total_products"],
            "total_stock": summary["total_stock"] or 0,
            "average_price": (
                round(average_price, 2)
                if average_price is not None
                else 0
            )
        })