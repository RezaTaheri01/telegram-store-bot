
# Telegram Bot with Django Integration

This bot is a Python-based Telegram bot integrated with a Django backend for database management, payment handling, product selling, and dynamic interaction features.

---

## Features

### Telegram Bot
- **User Account Management**:
  - Automatically creates a user account if it doesn't exist.
  - Retrieves and displays user balance.
  - Show user transactions.
  - Show user purchase. Todo
- **Interactive Menu**:
  - Main menu with options like **My Account**, **My Balance**, **Deposit**, and **Product Categories**.
  - Inline keyboards for seamless navigation.
- **Payment Handling**:
  - Generates unique payment links.
  - Processes payments via Django backend.
  - Updates user balance upon successful payment.
- **Product Management**:
  - Displays categories and products dynamically.
  - Supports product purchase via balance deduction.

### Django Backend
- **Database Models**:
  - `UserData`: Manages user account information.
  - `Transaction`: Tracks payment transactions.
  - `Category`, `Product`, `ProductDetail`: Manages products and their details.
- **Payment Processing**:
  - Creates dynamic payment links.
  - Updates database after payment confirmation.

---

## Installation

### Prerequisites
1. Python 3.8 or higher
2. Django (latest version recommended)
3. PostgreSQL or another preferred database system configured in Django [more info](https://docs.djangoproject.com/en/5.1/ref/databases/)
4. Libraries: `python-telegram-bot`, `asgiref`, `python-decouple`, etc.
5. Dependencies are listed in `req.txt`

### Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/RezaTaheri01/telegram-store-bot.git
   cd telegram-store-bot/telegram_store
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r req.txt
   ```

3. **Configure Django Settings**:
   - Set the `telegram_store.settings` module.
   - Configure your database in `settings.py`.

4. **Set Up Environment Variables**:
   - Create a `.env` file in the root directory with the following structure:
   ```env
   TOKEN=<your-telegram-bot-token>
   ```

5. **Migrate the Database**:
   ```bash
   python manage.py makemigrations payment users products
   python manage.py migrate
   ```

6. **Run the Django Development Server**:
   ```bash
   python manage.py runserver
   ```

7. **Run the Telegram Bot**:
   ```bash
   python bot.py
   ```

---

## Code Overview

### Telegram Bot

#### Key Features
- **Imports**:
  - `Django`: Sets up Django environment for database operations.
  - `telegram.ext`: Facilitates bot creation and updates handling.
- **Global Variables**:
  - `main_menu_keys`: Defines the main menu layout.
  - `textStart`, `textBalance`, etc.: Predefined messages for user interactions.
- **Core Functions**:
  - `start_menu`: Displays the main menu.
  - `check_create_account`: Automatically creates user accounts if they don't exist.
  - `user_balance`: Fetches and displays user balance.
  - `deposit_money`: Initiates the deposit process and generates payment links.
  - `charge_account`: Updates user balance upon successful payment.
  - `product_categories`: Displays product categories dynamically.
  - `products`: Lists products under a category.
  - `product_payment_detail`: Displays payment details for a product.
  - `payment`: Handles product purchase and balance deduction.

#### Conversation States
- `ENTER_AMOUNT`: Captures the deposit amount entered by the user.

#### Error Handling
- Logs all errors to `logs.log`.
- Notifies users about issues without disrupting the bot experience.

---

#### Payment Link Workflow
- Link Format: `http://127.0.0.1:8000/payment/confirm/?chat_id={chat_id}&user_id={user_id}&amount={amount}&bot_link={bot_link}&transaction={transaction}`.
- Redirects to a Django view for payment processing.

---

## Usage

1. **Start the Bot**:
   - Send `/start` to the bot.
   - Explore options like **My Account**, **My Balance**, **Deposit**, or **Product Categories**.

2. **Deposit Money**:
   - Select the **Deposit** option from the menu.
   - Enter the desired amount.
   - Click the payment link to complete the transaction.
   - Verify the updated balance in your account.

3. **Browse Products**:
   - Select **Product Categories** from the menu.
   - Choose a category and view the available products.
   - Purchase a product using your balance.

---

## Logs
- All errors are logged in `logs.log` with detailed messages.

---

## Notes
- Ensure the Django server is running for smooth payment processing.
- Update the `payment_url` in the bot code to match your server’s address when deploying.

---

## License
This project is licensed under the MIT License. See the `LICENSE` file for more details.
