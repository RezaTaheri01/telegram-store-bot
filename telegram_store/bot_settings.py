from telegram import InlineKeyboardButton, InlineKeyboardMarkup

categories_in_row = 1
products_in_row = 1
valid_link_in_seconds = 3600

# region Text messages
payment_url = "http://127.0.0.1:8000/payment/confirm/?chat_id={}&user_id={}&amount={}&bot_link={}&transition={}"
bot_link = "https://t.me/gameStorePersiaBot"

textError = "Something went wrong."
textStart = "Hello, {}!\nWelcome to Persia shop"  # username
textMenu = "Choose from below:"
textPriceUnit = "dollar"
textBalance = "Your current balance is {} {}."  # amount, price unit
textAmount = "Please enter the amount:"
textInvalidAmount = "Invalid input. Please enter a valid number:"
textChargeAccount = "Your account has been successfully charged {} {}."  # amount, price unit
textPaymentLink = f"Your payment link is ready and it's valid for {valid_link_in_seconds} hour."
textNoTransition = "No transition were founded"
textTransitions = "Here is your last 5 transitions:\n\n"
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
textProductList = "{} products"  # category name
textProductSoldOut = "This product is sold out or no longer available."
textPurchaseBill = "The {} costs {} {}."  # product name, price, price unit
textNotEnoughMoney = "Insufficient Funds"
textInvalidPaymentAmount = "Invalid payment amount! Please try again."
textProductDetail = "Successful\n{}"  # product.detail
# endregion

# region Buttons
buttonAccount = "Account Menu"
buttonBalance = "My Balance"
buttonCategories = "Product Categories"
buttonDeposit = "Deposit"
buttonAccountInfo = "Account Info"
buttonTransitionList = "Transitions List"
buttonBackMainMenu = "Main Menu"
buttonBack = "Back"

main_menu_button = InlineKeyboardButton(buttonBackMainMenu, callback_data="main_menu")
account_menu_button = InlineKeyboardButton(buttonAccount, callback_data="acc")

main_menu_keys = [
    [account_menu_button,
     InlineKeyboardButton(buttonBalance, callback_data="bala")],
    [InlineKeyboardButton(buttonCategories, callback_data="categories")],
    [InlineKeyboardButton(buttonDeposit, callback_data="deposit")],
]
main_menu_markup = InlineKeyboardMarkup(main_menu_keys)

back_menu_key = [
    [main_menu_button],
]
back_menu_markup = InlineKeyboardMarkup(back_menu_key)

account_keys = [
    [InlineKeyboardButton(buttonAccountInfo, callback_data="acc_info"),
     InlineKeyboardButton(buttonTransitionList, callback_data="trans_list")],
    [main_menu_button]
]
account_keys_markup = InlineKeyboardMarkup(account_keys)

# back to account menu
back_to_acc_key = [
    [account_menu_button,
     main_menu_button],
]
back_to_acc_markup = InlineKeyboardMarkup(back_to_acc_key)

back_to_cats_key = [[InlineKeyboardButton(buttonBack, callback_data='categories')]]
back_to_cats_markup = InlineKeyboardMarkup(back_to_cats_key)

# endregion
