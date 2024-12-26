from django.db import models
from users.models import UserData
from encrypted_json_fields.fields import EncryptedCharField


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Category Name")

    class Meta:
        verbose_name = "Product Category"
        verbose_name_plural = "Product Categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(to=Category, on_delete=models.SET_NULL, null=True, verbose_name="Category")
    name = models.CharField(max_length=100, verbose_name="Product Name")

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return self.name


class ProductDetail(models.Model):
    product = models.ForeignKey(to=Product, on_delete=models.SET_NULL, null=True, verbose_name="Product")
    # Todo: save details encrypted Done
    details = EncryptedCharField(max_length=200, verbose_name="Details")  # for example: user passwd
    price = models.IntegerField(verbose_name="Product Price")
    is_purchased = models.BooleanField(default=False, verbose_name="Is Purchased")
    purchase_date = models.DateTimeField(null=True, blank=True, verbose_name="Purchased  Date")
    buyer = models.ForeignKey(to=UserData, on_delete=models.SET_NULL, null=True, verbose_name="Buyer")

    class Meta:
        ordering = ['-is_purchased']  # show not purchased first
        verbose_name = "Product Detail"
        verbose_name_plural = "Products Detail"