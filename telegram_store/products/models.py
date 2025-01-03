from django.db import models
from users.models import UserData
from encrypted_json_fields.fields import EncryptedCharField
from telegram_store.settings import LANGUAGES


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=32, verbose_name="Category Name", unique=True, null=False)
    is_delete = models.BooleanField(default=False, blank=True)

    class Meta:
        verbose_name = "Product Category"
        verbose_name_plural = "Product Categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(to=Category, on_delete=models.SET_NULL, null=True, verbose_name="Category")
    name = models.CharField(max_length=32, verbose_name="Product Name", null=False)  # unique base on category
    price = models.IntegerField(verbose_name="Product Price")
    is_delete = models.BooleanField(default=False, blank=True)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        # unique base on category constraints
        constraints = [
            models.UniqueConstraint(
                fields=["category", f"name_{lang[0]}"],  # Use the language code from LANGUAGES
                name=f"unique_name_{lang[0]}_per_category"
            )
            for lang in LANGUAGES  # Iterate through LANGUAGES defined in settings
        ]

    def __str__(self):
        if self.category:
            return f"{self.name}({self.category.name})"
        return f"{self.name}"


class ProductDetail(models.Model):
    product = models.ForeignKey(to=Product, on_delete=models.SET_NULL, null=True, verbose_name="Product")
    # details are saved encrypted
    details = EncryptedCharField(max_length=256, verbose_name="Details")  # for example: user passwd
    is_purchased = models.BooleanField(default=False, verbose_name="Is Purchased")
    purchase_date = models.DateTimeField(null=True, blank=True, verbose_name="Purchased  Date")
    buyer = models.ForeignKey(to=UserData, on_delete=models.SET_NULL, null=True, verbose_name="Buyer")
    is_delete = models.BooleanField(default=False, blank=True)

    class Meta:
        ordering = ['-is_purchased']  # show not purchased first
        verbose_name = "Product Detail"
        verbose_name_plural = "Products Detail"

    def __str__(self):
        if self.product:
            return self.product.name
        return "None"
