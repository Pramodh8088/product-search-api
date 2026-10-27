from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "price",
        "category",
        "stock",
        "created_at",
    )

    search_fields = (
        "name",
        "description",
        "category",
    )

    list_filter = (
        "category",
        "created_at",
    )

    ordering = ("-created_at",)