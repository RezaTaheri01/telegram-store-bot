from telegram import InlineKeyboardButton, InlineKeyboardMarkup

categories_in_row = 1
products_in_row = 1
valid_link_in_seconds = 3600
lang = "en"  # default languages

# region Text messages
# Todo: improve payment url and fetch bot link automatically
payment_url = "http://127.0.0.1:8000/payment/confirm/?chat_id={}&user_id={}&amount={}&bot_link={}&transaction={}"
bot_link = "https://t.me/{}"  # bot username

textError = "Something went wrong."
textStart = "Hello, {}!\nWelcome to Persia shop"  # username
textMenu = "Choose from below:"
textPriceUnit = "dollar"
textBalance = "Your current balance is {} {}."  # amount, price unit
textAmount = "Please enter the amount:"
textInvalidAmount = "Invalid input. Please enter a valid number:"
textChargeAccount = "Your account has been successfully charged {} {}."  # amount, price unit
textPaymentLink = f"Your payment link is ready and it's valid for {valid_link_in_seconds // 3600} hour."
textNoTransaction = "No transactions were founded"
textTransaction = "Here is your last 5 transactions:\n\n"
textAccountMenu = "Hello, {}! How can I assist you today?"  # username
textAccInfo = "Username: {}\nFull name: {}\nBalance: {} {}"  # username, first name + last name, balance
textNotUser = "User not founded"
textPayButton = "Pay"
textNotFound = "Not founded"
textProductCategories = "Product categories"
textInvalidCategory = "Invalid category ID"
textNoProductFound = "No product found for this category"
textBackButton = "Back"
textInvalidProduct = "Invalid product ID! Please try again."
textProductList = "{}products"  # category name
textProductSoldOut = "This product is sold out or no longer available."
textPurchaseBill = "The {} costs {} {}."  # product name, price, price unit
textNotEnoughMoney = "Insufficient Funds"
textInvalidPaymentAmount = "Invalid payment amount! Please try again."
textProductDetail = "Successful\n{}"  # product.detail
textTransactionDetail = "Amount: {} {}\nDate: {}\n\n"  # amount, priceUnit, datetime
# endregion


# region Buttons
buttonAccount = "Account Menu"
buttonBalance = "My Balance"
buttonCategories = "Product Categories"
buttonDeposit = "Deposit"
buttonAccountInfo = "Account Info"
buttonTransactionsList = "Transactions List"
buttonBackMainMenu = "Main Menu"
buttonBack = "Back"

# The callbacks should be unique and short
main_menu_cb = "main_menu"
account_menu_cb = "account_menu"
account_info_cb = "account_info"
balance_cb = "balance"
categories_cb = "categories"
deposit_cb = "deposit"
transactions_cb = "transaction_list"
select_category_cb = "category"
select_product_cb = "product"
payment_cb = "payment"

main_menu_button = InlineKeyboardButton(buttonBackMainMenu, callback_data=main_menu_cb)
account_menu_button = InlineKeyboardButton(buttonAccount, callback_data=account_menu_cb)

main_menu_keys = [
    [account_menu_button,
     InlineKeyboardButton(buttonBalance, callback_data=balance_cb)],
    [InlineKeyboardButton(buttonCategories, callback_data=categories_cb)],
    [InlineKeyboardButton(buttonDeposit, callback_data=deposit_cb)],
]
main_menu_markup = InlineKeyboardMarkup(main_menu_keys)

back_menu_key = [
    [main_menu_button],
]
back_menu_markup = InlineKeyboardMarkup(back_menu_key)

account_keys = [
    [InlineKeyboardButton(buttonAccountInfo, callback_data=account_info_cb),
     InlineKeyboardButton(buttonTransactionsList, callback_data=transactions_cb)],
    [main_menu_button]
]
account_keys_markup = InlineKeyboardMarkup(account_keys)

# back to account menu
back_to_acc_key = [
    [account_menu_button,
     main_menu_button],
]
back_to_acc_markup = InlineKeyboardMarkup(back_to_acc_key)

back_to_cats_key = [[InlineKeyboardButton(buttonBack, callback_data=categories_cb)]]
back_to_cats_markup = InlineKeyboardMarkup(back_to_cats_key)

# endregion


# Todo: implement this individually for each user
# region Multi language
texts = {
    "en": {
        "textError": "Something went wrong.",
        "textStart": "Hello, {}!\nWelcome to Persia shop",  # username
        "textMenu": "Choose from below:",
        "textPriceUnit": "dollar",
        "textBalance": "Your current balance is {} {}.",  # amount, price unit
        "textAmount": "Please enter the amount:",
        "textInvalidAmount": "Invalid input. Please enter a valid number:",
        "textChargeAccount": "Your account has been successfully charged {} {}.",  # amount, price unit
        "textPaymentLink": f"Your payment link is ready and it's valid for {valid_link_in_seconds // 3600} hour.",
        "textNoTransaction": "No transactions were found",
        "textTransaction": "Here are your last 5 transactions:\n\n",
        "textAccountMenu": "Hello, {}! How can I assist you today?",  # username
        "textAccInfo": "Username: {}\nFull name: {}\nBalance: {} {}",  # username, full name, balance
        "textNotUser": "User not found",
        "textPayButton": "Pay",
        "textNotFound": "Not found",
        "textProductCategories": "Product categories",
        "textInvalidCategory": "Invalid category ID",
        "textNoProductFound": "No product found for this category",
        "textBackButton": "Back",
        "textInvalidProduct": "Invalid product ID! Please try again.",
        "textProductList": "{} products",  # category name
        "textProductSoldOut": "This product is sold out or no longer available.",
        "textPurchaseBill": "The {} costs {} {}.",  # product name, price, price unit
        "textNotEnoughMoney": "Insufficient funds",
        "textInvalidPaymentAmount": "Invalid payment amount! Please try again.",
        "textProductDetail": "Successful\n{}"  # product detail
    },
    "fa": {
        "textError": "مشکلی پیش آمده است.",
        "textStart": "سلام، {}!\nبه فروشگاه پرشیا خوش آمدید",  # username
        "textMenu": "از گزینه‌های زیر انتخاب کنید:",
        "textPriceUnit": "دلار",
        "textBalance": "موجودی فعلی شما {} {} است.",  # amount, price unit
        "textAmount": "لطفاً مقدار را وارد کنید:",
        "textInvalidAmount": "ورودی نامعتبر است. لطفاً یک عدد معتبر وارد کنید:",
        "textChargeAccount": "حساب شما با موفقیت به مقدار {} {} شارژ شد.",  # amount, price unit
        "textPaymentLink": f"لینک پرداخت شما آماده است و برای {valid_link_in_seconds // 3600} ساعت معتبر است.",
        "textNoTransaction": "هیچ تراکنشی یافت نشد",
        "textTransaction": "در اینجا ۵ تراکنش آخر شما آمده است:\n\n",
        "textAccountMenu": "سلام، {}! چگونه می‌توانم به شما کمک کنم؟",  # username
        "textAccInfo": "نام کاربری: {}\nنام کامل: {}\nموجودی: {} {}",  # username, full name, balance
        "textNotUser": "کاربر یافت نشد",
        "textPayButton": "پرداخت",
        "textNotFound": "یافت نشد",
        "textProductCategories": "دسته‌بندی محصولات",
        "textInvalidCategory": "شناسه دسته‌بندی نامعتبر است",
        "textNoProductFound": "محصولی برای این دسته‌بندی یافت نشد",
        "textBackButton": "بازگشت",
        "textInvalidProduct": "شناسه محصول نامعتبر است! لطفاً دوباره امتحان کنید.",
        "textProductList": "{} محصولات",  # category name
        "textProductSoldOut": "این محصول فروخته شده یا دیگر موجود نیست.",
        "textPurchaseBill": "{} به قیمت {} {}.",  # product name, price, price unit
        "textNotEnoughMoney": "موجودی کافی نیست",
        "textInvalidPaymentAmount": "مقدار پرداخت نامعتبر است! لطفاً دوباره امتحان کنید.",
        "textProductDetail": "موفقیت‌آمیز\n{}"  # product detail
    }
}
# endregion
