from django.contrib import admin
from . import models


# Register your models here.
@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['__str__']


# Register your models here.
@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'category']


# Register your models here.
@admin.register(models.ProductDetail)
class ProductDetailAdmin(admin.ModelAdmin):
    list_display = ['product', 'is_purchased', 'buyer']
    list_filter = ['product', 'is_purchased']
    readonly_fields = ['is_purchased', 'purchase_date', 'buyer']
