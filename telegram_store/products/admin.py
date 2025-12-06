from django.contrib import admin
from . import models
from telegram_store.settings import MODELTRANSLATION_LANGUAGES as langs


class ProductDetailInline(admin.TabularInline):
    model = models.ProductDetail
    extra = 1  # number of empty forms to display
    readonly_fields = ["is_purchased", "purchase_date", "buyer"]
    fields = ["details", "is_purchased", "purchase_date", "buyer"]
    can_delete = False

    def get_queryset(self, request):
        # Return empty queryset so no existing ProductDetails are shown
        return self.model.objects.none()



@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "is_delete"]
    readonly_fields = ["name"]
    list_filter = ["is_delete"]


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "order"]
    readonly_fields = ["name", "description"]
    list_editable = ["order"]
    ordering = ["category__name", "order"]
    inlines = [ProductDetailInline]
    search_fields = [
        f"category__name_{l}" for l in langs] + [f"name_{l}" for l in langs]
    list_filter = ["is_delete"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # ensure prefetch for category to optimize ordering
        return qs.select_related('category')


@admin.register(models.ProductDetail)
class ProductDetailAdmin(admin.ModelAdmin):
    list_display = ["product", "is_purchased", "buyer"]
    list_filter = ["is_purchased", "is_delete"]
    readonly_fields = ["is_purchased", "purchase_date", "buyer"]
    search_fields = [f"product__name_{l}" for l in langs]
