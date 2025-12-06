from django.db import models
from bot_settings import LANG1


class UserData(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)  # Telegram user ID
    first_name = models.CharField(max_length=64, null=True, blank=True)
    last_name = models.CharField(max_length=64, null=True, blank=True)
    mobile_number = models.CharField(max_length=16, null=True, blank=True)  # null because it may be hidden
    username = models.CharField(max_length=64, null=True, blank=True)  # telegram check username to be unique
    balance = models.DecimalField(max_digits=18, decimal_places=2, default=0.0, db_index=True)
    language = models.CharField(max_length=8, default=LANG1, verbose_name='Language')
    utc_offset = models.FloatField(default=0.0)  # +3:30 => +3.5

    def __str__(self):
        # if username not founded using full name
        if self.username:
            return f"{self.username}"
        return f"{self.first_name or ''} {self.last_name or ''}".strip()

    class Meta:
        verbose_name = "User Data"
        verbose_name_plural = "Users Data"


class BotSettings(models.Model):
    # UI layout settings
    category_in_row = models.PositiveIntegerField(
        verbose_name="Categories in Row",
        help_text="Number of category buttons per row."
    )
    product_in_row = models.PositiveIntegerField(
        verbose_name="Products in Row",
        help_text="Number of product buttons per row."
    )
    number_of_transactions = models.PositiveIntegerField(
        verbose_name="Num of Transaction",
        help_text="Transactions shown per page in history."
    )
    number_of_product = models.PositiveIntegerField(
        verbose_name="Num of Products in Purchase",
        help_text="Purchase history displayed per page."
    )

    # Currency
    wallet_currency = models.CharField(
        max_length=8,
        verbose_name="Wallet Currency",
        help_text="Ex: USD, RUB, CAD, ..."
    )
    wallet_currency_sign = models.CharField(
        max_length=8,
        verbose_name="Wallet Currency Sign",
        help_text="Ex: $, ₽, ..."
    )

    # TON pricing + fetching
    ton_price_delay = models.PositiveIntegerField(
        verbose_name="TON Price Delay (seconds)",
        help_text="Interval between price updates in seconds."
    )
    ton_fetch_limit = models.PositiveIntegerField(
        verbose_name="TON Fetch Limit",
        help_text="Number of transactions fetched per request.\nlimit should be less or equal 1000"
    )
    ton_network_delay = models.PositiveIntegerField(
        verbose_name="TON Network Delay (seconds)",
        help_text="Interval between deposit address checks(Fetch transactions)"
    )
    
    failed_transactions_delay = models.PositiveIntegerField(
        verbose_name="Failed Transactions Delay (seconds)",
        help_text="Interval between checking failed transactions."
    )

    # TON credentials
    ton_deposit_address = models.CharField(max_length=256, verbose_name="TON Deposit Address")
    ton_network_api_key = models.CharField(
        max_length=256,
        verbose_name="TON Network API Key",
        help_text="Provided by @tonapibot"
    )
    
    cmc_api_key = models.CharField(max_length=256, verbose_name="CoinMarketCap API Key",
                                   help_text="Get api key from https://coinmarketcap.com/api/pricing/")
    
    telegram_wallet_link = models.CharField(max_length=256, verbose_name="@Wallet",
                                            default="https://t.me/wallet/start?startapp=tonspace_main")

    disable_product_images = models.BooleanField(
        verbose_name="Disable Product Images",
        default=True,
        help_text="Enable this to hide product images for a cleaner interface and faster loading."
    )

    class Meta:
        verbose_name = "Bot Settings"
        verbose_name_plural = "Bot Settings"

    # (Optional) enforce only one settings row exists
    def save(self, *args, **kwargs):
        if not self.pk and BotSettings.objects.exists():
            raise ValueError("Only one BotSettings instance allowed.")
        return super().save(*args, **kwargs)

    def __str__(self):
        return "Bot Configuration"

    