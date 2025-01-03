from modeltranslation.translator import TranslationOptions, register
from .models import Category, Product
from telegram_store.settings import MODELTRANSLATION_LANGUAGES


@register(Product)
class AccountTranslationOptions(TranslationOptions):
    fields = ['name']
    required_languages = MODELTRANSLATION_LANGUAGES # Make these non-nullable


@register(Category)
class AccountTranslationOptions(TranslationOptions):
    fields = ['name']
    required_languages = MODELTRANSLATION_LANGUAGES  # Make these non-nullable
