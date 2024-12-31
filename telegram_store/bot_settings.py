from telegram import InlineKeyboardButton, InlineKeyboardMarkup

categories_in_row = 1  # number of categories in row
products_in_row = 1  # number of products in row
number_of_transaction = 10  # number of transactions in transactions list
valid_link_in_seconds = 3600  # 1 hour

# For more than 2 languages you need to add field to product.model category and product
# also add your language in bot.py get_name, change_language functions
lang1, lang2 = "en", "fa"
# aging_limit = 1  # days

# Todo: improve payment url
payment_url = "http://127.0.0.1:8000/payment/confirm/?chat_id={}&user_id={}&amount={}&bot_link={}&transaction={}"
bot_link = "https://t.me/{}"  # bot username

# region Multi language texts
texts = {
    lang1: {
        "textError": "Something went wrong",
        "textStart": "Hello, {}!\nWelcome to Persia shop",  # username
        "textMenu": "Please choose from below:",
        "textPriceUnit": "dollar",
        "textBalance": "Your current balance is {} {}",  # amount, price unit
        "textAmount": "Please enter the amount:",
        "textInvalidAmount": "Invalid input. Please enter a valid number:",
        "textChargeAccount": "Your account has been successfully charged {} {}",  # amount, price unit
        "textPaymentLink": f"Your payment link is ready and it's valid for {valid_link_in_seconds // 3600} hour",
        "textNoTransaction": "No transactions were found",
        "textTransaction": f"Here are your last {number_of_transaction} transactions:\n\n",
        "textAccountMenu": "Hello, {}! How can I assist you today?",  # username
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
        # Button texts
        "buttonAccount": "Account Menu",
        "buttonBalance": "My Balance",
        "buttonCategories": "Product Categories",
        "buttonDeposit": "Deposit",
        "buttonAccountInfo": "Account Info",
        "buttonTransactionsList": "Transactions List",
        "buttonBackMainMenu": "Main Menu",
        "buttonBack": "Back",
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
        "textPaymentLink": f"لینک پرداخت شما آماده است و برای {valid_link_in_seconds // 3600} ساعت معتبر است.",
        "textNoTransaction": "هیچ تراکنشی یافت نشد",
        "textTransaction": f"در اینجا {number_of_transaction} تراکنش آخر شما آمده است:\n\n",
        "textAccountMenu": "سلام، {}! چگونه می‌توانم به شما کمک کنم؟",  # username
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
        # Button texts
        "buttonAccount": "منوی اکانت",
        "buttonBalance": "موجودی",
        "buttonCategories": "دسته بندی محصولات",
        "buttonDeposit": "افزایش موجودی",
        "buttonAccountInfo": "جزِئیات اکانت",
        "buttonTransactionsList": "لیست تراکنش ها",
        "buttonBackMainMenu": "منوی اصلی",
        "buttonBack": "بازگشت",
        "buttonLanguage": lang1,  # don't change this
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
transactions_cb = "6"
change_lang_cb = "7"
# Do not use _ in below callbacks
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
        [InlineKeyboardButton(texts[key]["buttonLanguage"
                                         ""], callback_data=change_lang_cb)],
        [InlineKeyboardButton(texts[key]["buttonDeposit"], callback_data=deposit_cb)],
    ]
    buttons[key]["main_menu_markup"] = InlineKeyboardMarkup(main_menu_keys)

    back_menu_key = [
        [main_menu_button],
    ]
    buttons[key]["back_menu_markup"] = InlineKeyboardMarkup(back_menu_key)

    account_keys = [
        [InlineKeyboardButton(texts[key]["buttonAccountInfo"], callback_data=account_info_cb),
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
