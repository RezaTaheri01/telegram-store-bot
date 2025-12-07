"""
Steps to add a new language:(also you can remove language by these steps)

1. Update line 109 in `telegram_store/settings.py` to include the new language, following the format used for existing entries.
2. Add the `lang<num>` entry below and ensure the `texts` dictionary reflects the new language.
3. Run the following commands to apply migrations:
   a. `python manage.py makemigrations payment users products`
   b. `python manage.py migrate`
4. In the domain admin panel, populate the new fields for product categories and products with the appropriate data for the new language.
5. update prepopulated_fields in ProductAdmin and CategoryAdmin base on your languages at products/admin .py
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from decouple import config

# lang1 is your primary language
# base on languages in telegram_store/setting.py
LANG1, LANG2 = "ru", "en"

TOKEN = config("TOKEN", default="")
UPDATE_SETTING_COMMAND = config("UPDATE_SETTING_COMMAND", default="update")
SITE_DOMAIN = config("SITE_DOMAIN", default=None)

SEP_LINE = "\n`" + "_" * 30 + "`\n\n"
SEP_LINE_HTML = "\n" + "_" * 40 + "\n\n"

# region Multi language texts
# Attention the order of languages are important(should be same as lang and line 109 in telegram_store/setting.py)
# Wrap in backticks ` to prevent any Markdown parsing
texts = {
    LANG1: {
        "textError": "⚠️ Произошла ошибка. Попробуйте снова",
        "textErrorNoPrice": "⚠️ Не удалось получить цену TON. Переводы временно недоступны. Пожалуйста, попробуйте позже",
        "textStart": "👋 Привет, {}!\n📋 Пожалуйста, выберите вариант ниже:",
        "textMenu": "📋 Пожалуйста, выберите вариант ниже:",
        "textBalance": "💰 Ваш текущий баланс: {} {}",
        "textAmount": "🔢 Введите сумму:",
        "textInvalidAmount": "❗ Неверный ввод. Пожалуйста, введите корректное число",
        "textChargeAccount": "🎉 *Ваш аккаунт пополнен на* `{}` *TON*\n\n💱 *Курс:* 1 TON = `{}` {}",
        "textPaymentLink": (
            "💎 Отправьте TON на этот адрес:\n\n`{}`\n\n"
            "💬 С этим комментарием:\n\n`{}`\n\n"
            "💱 *Курс обмена:* 1 TON = `{}` {}\n\n"
            "⚠️ Перед отправкой всегда заново открывайте страницу Пополнения (/pay)."
        ),
        "textNoTransaction": "📭 Транзакции не найдены",
        "textTransaction": "📄 Ваши транзакции, страница {}:",
        "textProducts": "🛍 Ваши покупки, страница {}:",
        "textAccountMenu": "👤 Привет, {}! Выберите действие:",
        "textAccInfo": "👤 Имя пользователя: {}\n📛 Полное имя: {}\n💰 Баланс: {} {}",
        "textNotUser": "❌ Пользователь не найден",
        "textPayButton": "💳 Оплатить",
        "textNotFound": "🔍 Не найдено",
        "textProductCategories": "📂 Категории товаров",
        "textInvalidCategory": "❗ Неверный ID категории",
        "textNoProductFound": "🚫 Товары не найдены",
        "textBackButton": "↩️ Назад",
        "textInvalidProduct": "❗ Неверный ID товара. Попробуйте снова",
        "textProductList": "📦 {} товаров доступно",
        "textProductSoldOut": "❗ Товар недоступен или распродан",
        "textPurchaseBill": "🛒 {}\n💰 Цена: {} {}\n🔑 В наличии: {}",
        "textPurchaseUpdateAvailable": "🔑 В наличии: {}",
        "textNotEnoughMoney": "💸 Недостаточно средств",
        "textInvalidPaymentAmount": "⚠️ Неверная сумма платежа, попробуйте ещё раз",
        "textProductDetail": "✅ Покупка успешна!\n\n🔑 {}",
        "textPaymentFailed": "❌ Платеж не прошел. Пожалуйста, попробуйте снова",
        "textTransactionDetail": "💱 *Курс:* 1 TON = `{}` {}\n🆔 Транзакция: `{}`\n💳 Сумма: `{}` TON\n📅 Дата: {}{}",
        "textProductDetailList": "🛍 Товар: {}\n📅 Дата: {}{}\n📦 Детали: `{}`",
        "textPrev": "⬅️ Предыдущая",
        "textNext": "➡️ Следующая",
        "textTimezone": "🌍 Отправьте местоположение для установки часового пояса",
        "textTimezoneSuccess": "⏱ Часовой пояс обновлен!",
        "textTimezoneFailed": "⚠️ Не удалось обновить. Попробуйте позже",
        "buttonAccount": "👤 Аккаунт",
        "buttonBalance": "💰 Баланс",
        "buttonCategories": "📂 Категории",
        "buttonDeposit": "➕ Пополнить",
        "buttonAccountInfo": "🔎 Информация",
        "buttonTransactionsList": "📄 История транзакций",
        "buttonBackMainMenu": "🏠 Главное меню",
        "buttonBack": "↩️ Назад",
        "buttonProductsList": "🛍 История покупок",
        "telegramWallet": "💸 Оплатить через @Wallet",
        "buttonLanguage": LANG2,
    },
    LANG2: {
        "textError": "⚠️ An error occurred. Please try again",
        "textErrorNoPrice": "⚠️ Unable to retrieve TON price. Transfers are temporarily unavailable. Please try again later",
        "textStart": "👋 Hello, {}!\n📋 Please choose an option below:",
        "textMenu": "📋 Please choose an option below:",
        "textBalance": "💰 Your current balance: {} {}",
        "textAmount": "🔢 Enter the amount:",
        "textInvalidAmount": "❗ Invalid input. Please enter a valid number",
        "textChargeAccount": "🎉 *Your account was credited with* `{}` *TON*\n\n💱 *Exchange rate:* 1 TON = `{}` {}",
        "textPaymentLink": (
            "💎 Send TON to this address:\n\n`{}`\n\n"
            "💬 With this comment:\n\n`{}`\n\n"
            "💱 *Exchange rate:* 1 TON = `{}` {}\n\n"
            "⚠️ Always re-check the Deposit page before sending (/pay)."
        ),
        "textNoTransaction": "📭 No transactions found",
        "textTransaction": "📄 Your transactions, page {}:",
        "textProducts": "🛍 Your purchases, page {}:",
        "textAccountMenu": "👤 Please choose an option:",
        "textAccInfo": "👤 Username: {}\n📛 Full Name: {}\n💰 Balance: {} {}",
        "textNotUser": "❌ User not found",
        "textPayButton": "💳 Pay",
        "textNotFound": "🔍 Not found",
        "textProductCategories": "📂 Product Categories",
        "textInvalidCategory": "❗ Invalid category ID",
        "textNoProductFound": "🚫 No products in this category",
        "textBackButton": "↩️ Back",
        "textInvalidProduct": "❗ Invalid product ID. Try again",
        "textProductList": "📦 {} products available",
        "textProductSoldOut": "❗ This product is sold out or unavailable",
        "textPurchaseBill": "🛒 {}\n💰 Price: {} {}\n🔑 Available: {}",
        "textPurchaseUpdateAvailable": "🔑 Available: {}",
        "textNotEnoughMoney": "💸 Insufficient funds",
        "textInvalidPaymentAmount": "⚠️ Invalid payment amount, try again",
        "textProductDetail": "✅ Purchase successful!\n\n🔑 {}",
        "textPaymentFailed": "❌ Payment failed. Please try again",
        "textTransactionDetail": "💱 *Exchange rate:* 1 TON = `{}` {}\n🆔 Tx: `{}`\n💳 Amount: `{}` TON\n📅 Date: {}{}",
        "textProductDetailList": "🛍 Product: {}\n📅 Date: {}{}\n📦 Details: `{}`",
        "textPrev": "⬅️ Previous",
        "textNext": "➡️ Next",
        "textTimezone": "🌍 Send your location to set your timezone",
        "textTimezoneSuccess": "⏱ Timezone updated!",
        "textTimezoneFailed": "⚠️ Failed to update. Try again",
        "buttonAccount": "👤 Account",
        "buttonBalance": "💰 My Balance",
        "buttonCategories": "📂 Categories",
        "buttonDeposit": "➕ Deposit",
        "buttonAccountInfo": "🔎 Account Info",
        "buttonTransactionsList": "📄 Transaction History",
        "buttonBackMainMenu": "🏠 Main Menu",
        "buttonBack": "↩️ Back",
        "buttonProductsList": "🛍 Purchase History",
        "telegramWallet": "💸 Pay with @Wallet",
        "buttonLanguage": LANG1,
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
    main_menu_button = InlineKeyboardButton(
        texts[key]["buttonBackMainMenu"], callback_data=main_menu_cb)
    account_menu_button = InlineKeyboardButton(
        texts[key]["buttonAccount"], callback_data=account_menu_cb)

    balance_keys = [[InlineKeyboardButton(
        texts[key]["buttonDeposit"], callback_data=deposit_cb)], [main_menu_button]]
    buttons[key]["balance_markup"] = InlineKeyboardMarkup(balance_keys)

    main_menu_keys = [
        [account_menu_button,
         InlineKeyboardButton(texts[key]["buttonBalance"], callback_data=balance_cb)],
        [InlineKeyboardButton(texts[key]["buttonCategories"],
                              callback_data=categories_cb)],
        [InlineKeyboardButton(texts[key]["buttonLanguage"],
                              callback_data=change_lang_cb)],
        [InlineKeyboardButton(texts[key]["buttonDeposit"],
                              callback_data=deposit_cb)],
    ]
    buttons[key]["main_menu_markup"] = InlineKeyboardMarkup(main_menu_keys)

    back_menu_key = [
        [main_menu_button],
    ]
    buttons[key]["back_menu_markup"] = InlineKeyboardMarkup(back_menu_key)

    account_keys = [
        [InlineKeyboardButton(texts[key]["buttonAccountInfo"],
                              callback_data=account_info_cb)],
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

    back_to_cats_key = [[InlineKeyboardButton(
        texts[key]["buttonBack"], callback_data=categories_cb)]]
    buttons[key]["back_to_cats_markup"] = InlineKeyboardMarkup(
        back_to_cats_key)
# endregion
