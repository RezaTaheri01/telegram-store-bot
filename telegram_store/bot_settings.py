"""
Steps to add a new language:(also you can remove language by these steps)

1. Update line 109 in `telegram_store/settings.py` to include the new language, following the format used for existing entries.
2. Add the `lang<num>` entry below and ensure the `texts` dictionary reflects the new language.
3. Run the following commands to apply migrations:
   a. `python manage.py makemigrations payment users products`
   b. `python manage.py migrate`
4. In the domain admin panel, populate the new fields for product categories and products with the appropriate data for the new language.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from decouple import config

categories_in_row = 2  # number of categories in row
products_in_row = 2  # number of products in row
number_of_transaction = 4  # number of transactions in transactions list
number_of_products = 2  # number of products in purchase product list
valid_link_in_seconds = 1800  # 30 minutes
time_zone = "UTC"  # base on TIME_ZONE in telegram_store/setting.py

# lang1 is your primary language
lang1, lang2, lang3 = "en", "fa", "du"  # base on languages in telegram_store/setting.py

# modify payment_url your base on your domain, just this part(http://127.0.0.1:8000)
payment_url = config("PAYMENT_DOMAIN") + "/payment/confirm/?chat_id={}&user_id={}&amount={}&bot_link={}&transaction={}"
bot_link = "https://t.me/{}"  # bot username

# region Multi language texts
# Attention the order of languages are important(should be same as lang and line 109 in telegram_store/setting.py)
texts = {
    lang1: {
        "textError": "Something went wrong",
        "textStart": "Hello, {}!\nWelcome to Persia shop",  # username
        "textMenu": "Please choose from below",
        "textPriceUnit": "Dollar",
        "textBalance": "Your current balance is {} {}",  # amount, price unit
        "textAmount": "Please enter the amount:",
        "textInvalidAmount": "Invalid input. Please enter a valid number:",
        "textChargeAccount": "Your account has been successfully charged {} {}",  # amount, price unit
        "textPaymentLink": f"Your payment link is ready and it's valid for {valid_link_in_seconds // 60} minutes",
        "textNoTransaction": "No transactions were found",
        "textTransaction": "Here are your transactions, page {}:",
        "textProducts": "Here are your purchases, page {}:",
        "textAccountMenu": "Hey {}! Please choose from below",  # username
        "textAccInfo": "Username: {}\nFull name: {}\nBalance: {} {}",  # username, full name, balance
        "textNotUser": "User not found",
        "textPayButton": "Pay",
        "textNotFound": "Not found",
        "textProductCategories": "Product categories",
        "textInvalidCategory": "Invalid category ID",
        "textNoProductFound": "No product found for this category",
        "textBackButton": "Back",
        "textInvalidProduct": "Invalid product ID! Please try again",
        "textProductList": "{} products",  # category name
        "textProductSoldOut": "This product is sold out or no longer available",
        "textPurchaseBill": "The {} costs {} {}",  # product name, price, price unit
        "textNotEnoughMoney": "Insufficient funds",
        "textInvalidPaymentAmount": "Invalid payment amount! Please try again",
        "textProductDetail": "Successful\n{}",  # product detail
        "textTransactionDetail": "Amount: {} {}\nDate: {}\n\n",  # amount, priceUnit, datetime
        "textProductDetailList": "Product: {}\nDate: {}\nDetail: {}\n\n",  # Product Name, Purchase Date, Detail
        "textPrev": "Prev",
        "textNext": "Next",
        # Button texts
        "buttonAccount": "Account Menu",
        "buttonBalance": "My Balance",
        "buttonCategories": "Product Categories",
        "buttonDeposit": "Deposit",
        "buttonAccountInfo": "Account Info",
        "buttonTransactionsList": "Transactions List",
        "buttonBackMainMenu": "Main Menu",
        "buttonBack": "Back",
        "buttonProductsList": "Purchase History",
        "buttonLanguage": lang2,  # don't change this
    },
    lang2: {
        "textError": "مشکلی پیش آمده است",
        "textStart": "سلام {}\nبه فروشگاه پرشیا خوش آمدید",  # username
        "textMenu": "از گزینه‌های زیر انتخاب کنید:",
        "textPriceUnit": "دلار",
        "textBalance": "موجودی فعلی شما {} {} است",  # amount, price unit
        "textAmount": "لطفاً مقدار را وارد کنید:",
        "textInvalidAmount": "ورودی نامعتبر است. لطفاً یک عدد معتبر وارد کنید:",
        "textChargeAccount": "حساب شما با موفقیت به مقدار {} {} شارژ شد",  # amount, price unit
        "textPaymentLink": f"لینک پرداخت شما آماده است و برای {valid_link_in_seconds // 60} دقیقه معتبر است.",
        "textNoTransaction": "هیچ تراکنشی یافت نشد",
        "textTransaction": "تراکنش های شما, صفحه {}",
        "textProducts": "محصولات خریداری شده شما, صفحه {}",
        "textAccountMenu": "درود مجدد {}! لطفا از گزینه های زیر انتخاب کنید",  # username
        "textAccInfo": "نام کاربری: {}\nنام کامل: {}\nموجودی: {} {}",  # username, full name, balance
        "textNotUser": "کاربر یافت نشد",
        "textPayButton": "پرداخت",
        "textNotFound": "یافت نشد",
        "textProductCategories": "دسته‌بندی محصولات",
        "textInvalidCategory": "شناسه دسته‌بندی نامعتبر است",
        "textNoProductFound": "محصولی برای این دسته‌بندی یافت نشد",
        "textBackButton": "بازگشت",
        "textInvalidProduct": "شناسه محصول نامعتبر است! لطفاً دوباره امتحان کنید",
        "textProductList": "محصولات {}",  # category name
        "textProductSoldOut": "این محصول فروخته شده یا دیگر موجود نیست",
        "textPurchaseBill": "{} به قیمت {} {}",  # product name, price, price unit
        "textNotEnoughMoney": "موجودی کافی نیست",
        "textInvalidPaymentAmount": "مقدار پرداخت نامعتبر است! لطفاً دوباره امتحان کنید",
        "textProductDetail": "موفقیت ‌آمیز\n{}",  # product detail
        "textTransactionDetail": "مقدار: {} {}\nتاریخ: {}\n\n",  # amount, priceUnit, datetime
        "textProductDetailList": "محصول: {}\nتاریخ خرید: {}\nجزئیات: {}\n\n",  # Product Name, Purchase Date, Detail
        "textPrev": "قبلی",
        "textNext": "بعدی",
        # Button texts
        "buttonAccount": "منوی اکانت",
        "buttonBalance": "موجودی",
        "buttonCategories": "دسته بندی محصولات",
        "buttonDeposit": "افزایش موجودی",
        "buttonAccountInfo": "جزِئیات اکانت",
        "buttonTransactionsList": "لیست تراکنش ها",
        "buttonBackMainMenu": "منوی اصلی",
        "buttonBack": "بازگشت",
        "buttonProductsList": "تاریخچه محصولات",
        "buttonLanguage": lang3,  # don't change this
    },
    lang3: {
        "textError": "Etwas ist schiefgelaufen",
        "textStart": "Hallo, {}!\nWillkommen im Persia Shop",  # username
        "textMenu": "Bitte wählen Sie aus den folgenden Optionen",
        "textPriceUnit": "Dollar",
        "textBalance": "Ihr aktuelles Guthaben beträgt {} {}",  # amount, price unit
        "textAmount": "Bitte geben Sie den Betrag ein:",
        "textInvalidAmount": "Ungültige Eingabe. Bitte geben Sie eine gültige Zahl ein:",
        "textChargeAccount": "Ihr Konto wurde erfolgreich mit {} {} aufgeladen",  # amount, price unit
        "textPaymentLink": f"Ihr Zahlungslink ist bereit und für {valid_link_in_seconds // 60} Minuten gültig",
        "textNoTransaction": "Es wurden keine Transaktionen gefunden",
        "textTransaction": "Hier sind Ihre Transaktionen, Seite {}:",
        "textProducts": "Hier sind Ihre Produkte, Seite {}:",
        "textAccountMenu": "Hallo {}! Bitte wählen Sie aus den folgenden Optionen",  # username
        "textAccInfo": "Benutzername: {}\nVollständiger Name: {}\nGuthaben: {} {}",  # username, full name, balance
        "textNotUser": "Benutzer nicht gefunden",
        "textPayButton": "Bezahlen",
        "textNotFound": "Nicht gefunden",
        "textProductCategories": "Produktkategorien",
        "textInvalidCategory": "Ungültige Kategorie-ID",
        "textNoProductFound": "Für diese Kategorie wurden keine Produkte gefunden",
        "textBackButton": "Zurück",
        "textInvalidProduct": "Ungültige Produkt-ID! Bitte versuchen Sie es erneut",
        "textProductList": "{} Produkte",  # category name
        "textProductSoldOut": "Dieses Produkt ist ausverkauft oder nicht mehr verfügbar",
        "textPurchaseBill": "Das {} kostet {} {}",  # product name, price, price unit
        "textNotEnoughMoney": "Unzureichende Mittel",
        "textInvalidPaymentAmount": "Ungültiger Zahlungsbetrag! Bitte versuchen Sie es erneut",
        "textProductDetail": "Erfolgreich\n{}",  # product detail
        "textTransactionDetail": "Betrag: {} {}\nDatum: {}\n\n",  # amount, priceUnit, datetime
        "textProductDetailList": "Produkte: {}\nDatum: {}\nEinzelheit: {}\n\n",
        # Product Name, Purchase Date, Detail
        "textPrev": "Vorh",
        "textNext": "Nächste",
        # Button texts
        "buttonAccount": "Kontomenü",
        "buttonBalance": "Mein Guthaben",
        "buttonCategories": "Produktkategorien",
        "buttonDeposit": "Einzahlen",
        "buttonAccountInfo": "Kontoinformationen",
        "buttonTransactionsList": "Transaktionsliste",
        "buttonBackMainMenu": "Hauptmenü",
        "buttonBack": "Zurück",
        "buttonProductsList": "Produkte",
        "buttonLanguage": lang1,  # Don't change this
    }
}
# endregion


# region multi language buttons
main_menu_cb = "0"
account_menu_cb = "1"
account_info_cb = "2"
balance_cb = "3"
categories_cb = "4"
deposit_cb = "5"
change_lang_cb = "6"
# Warning: Do not use _ in below callbacks!
transactions_cb = "tran"
purchase_products_cb = "pp"
select_category_cb = "cat"
select_product_cb = "pro"
payment_cb = "pay"

buttons: dict = {key: {} for key in texts.keys()}

for key, value in texts.items():
    main_menu_button = InlineKeyboardButton(texts[key]["buttonBackMainMenu"], callback_data=main_menu_cb)
    account_menu_button = InlineKeyboardButton(texts[key]["buttonAccount"], callback_data=account_menu_cb)

    main_menu_keys = [
        [account_menu_button,
         InlineKeyboardButton(texts[key]["buttonBalance"], callback_data=balance_cb)],
        [InlineKeyboardButton(texts[key]["buttonCategories"], callback_data=categories_cb)],
        [InlineKeyboardButton(texts[key]["buttonLanguage"], callback_data=change_lang_cb)],
        [InlineKeyboardButton(texts[key]["buttonDeposit"], callback_data=deposit_cb)],
    ]
    buttons[key]["main_menu_markup"] = InlineKeyboardMarkup(main_menu_keys)

    back_menu_key = [
        [main_menu_button],
    ]
    buttons[key]["back_menu_markup"] = InlineKeyboardMarkup(back_menu_key)

    account_keys = [
        [InlineKeyboardButton(texts[key]["buttonAccountInfo"], callback_data=account_info_cb)],
        [InlineKeyboardButton(texts[key]["buttonProductsList"], callback_data=purchase_products_cb),
         InlineKeyboardButton(texts[key]["buttonTransactionsList"], callback_data=transactions_cb)],
        [main_menu_button]
    ]
    buttons[key]["account_keys_markup"] = InlineKeyboardMarkup(account_keys)

    # back to account menu
    back_to_acc_key = [
        [account_menu_button,
         main_menu_button],
    ]
    buttons[key]["back_to_acc_markup"] = InlineKeyboardMarkup(back_to_acc_key)

    back_to_cats_key = [[InlineKeyboardButton(texts[key]["buttonBack"], callback_data=categories_cb)]]
    buttons[key]["back_to_cats_markup"] = InlineKeyboardMarkup(back_to_cats_key)

# endregion
