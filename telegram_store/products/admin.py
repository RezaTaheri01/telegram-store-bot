from django.contrib import admin
from . import models


# Register your models here.
@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["__str__"]
    readonly_fields = ["name"]


# Register your models here.
@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["__str__", "category", "order"]
    readonly_fields = ["name", "description"]
    list_filter = ["category"]
    list_editable = ["order"]
    ordering = ["order"]
    

# Register your models here.
@admin.register(models.ProductDetail)
class ProductDetailAdmin(admin.ModelAdmin):
    list_display = ["product", "is_purchased", "buyer"]
    list_filter = ["product", "is_purchased"]
    readonly_fields = ["is_purchased", "purchase_date", "buyer"]
    
