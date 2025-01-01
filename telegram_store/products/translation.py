from modeltranslation.translator import TranslationOptions, register
from .models import Category, Product


@register(Product)
class AccountTranslationOptions(TranslationOptions):
    fields = ['name']


@register(Category)
class AccountTranslationOptions(TranslationOptions):
    fields = ['name']
