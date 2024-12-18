# Telegram Bot with Django Integration

This bot is a Python-based Telegram bot integrated with a Django backend for database management and payment handling. Below is an overview of the bot's functionality, setup instructions, and its interaction with the Django backend.

---

## Features

### Telegram Bot
- **User Account Management**:
  - Automatically creates a user account if it doesn't exist.
  - Retrieves and displays user balance.
- **Interactive Menu**:
  - Main menu with options like **My Account**, **My Balance**, and **Deposit**.
  - Inline keyboards for seamless navigation.
- **Payment Handling**:
  - Generates unique payment links.
  - Processes payments via Django backend.
  - Updates user balance upon successful payment.

### Django Backend
- **Database Models**:
  - `UserData`: Manages user account information.
  - `Transitions`: Tracks payment transactions.
- **Payment Processing**:
  - Creates dynamic payment links.
  - Updates database after payment confirmation.

---

## Installation

### Prerequisites
1. Python 3.8 or higher
2. Django (latest version recommended)
3. PostgreSQL or another preferred database system configured in Django
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
   - Add `users` and `payment` apps to `INSTALLED_APPS`.
   - Configure your database in `settings.py`.

4. **Set Up Environment Variables**:
   - Create a `.env` file in the root directory with the following structure:
   ```env
   TOKEN=<your-telegram-bot-token>
   ```

5. **Migrate the Database**:
   ```bash
   python manage.py makemigrations payment users
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

#### Conversation States
- `ENTER_AMOUNT`: Captures the deposit amount entered by the user.

#### Error Handling
- Logs all errors to `logs.log`.
- Notifies users about issues without disrupting the bot experience.

---

#### Payment Link Workflow
- Link Format: `http://127.0.0.1:8000/payment/confirm/?chat_id={chat_id}&user_id={user_id}&amount={amount}&bot_link={bot_link}&transition={transition}`.
- Redirects to a Django view for payment processing.

---

## Usage

1. **Start the Bot**:
   - Send `/start` to the bot.
   - Explore options like **My Account**, **My Balance**, or **Deposit**.

2. **Deposit Money**:
   - Select the **Deposit** option from the menu.
   - Enter the desired amount.
   - Click the payment link to complete the transaction.
   - Verify the updated balance in your account.

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
