from django.urls import path

from .views import (
    ProductListCreateView,
    ProductDetailView,
    ProductSummaryView,
)


urlpatterns = [
    path(
        "products/",
        ProductListCreateView.as_view(),
        name="product-list-create",
    ),
    path(
        "products/summary/",
        ProductSummaryView.as_view(),
        name="product-summary",
    ),
    path(
        "products/<int:pk>/",
        ProductDetailView.as_view(),
        name="product-detail",
    ),
]