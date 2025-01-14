# Telegram Bot with Django Integration 📢💻

This bot is a Python-based Telegram bot seamlessly integrated with a Django backend. It supports database management, payment handling, digital product selling, and dynamic user interactions.

---

## Features 🏢

### Telegram Bot 📲

- **Multi-language Support**:
  - Currently supports three languages, with the ability to add more.(There is a help comment in bot_settings.py)
  - Users can change the language via the main menu.

- **User Account Management**:
  - Automatically creates user accounts if they don’t exist.
  - Retrieves and displays user balance. 💳
  - Displays user transaction history. 🔄

- **Interactive Menu**:
  - Provides options like **My Account**, **My Balance**, **Deposit**, and **Product Categories**.
  - Includes inline keyboards for seamless navigation. 📝

- **Payment Handling**:
  - Generates unique payment links. 📡
  - Processes payments via the Django backend.
  - Updates user balance upon successful payment. ✔️

- **Product Management**:
  - Dynamically displays categories and products. 🛒
  - Supports product purchases via balance deduction. 💸

- **Customization**:
  - In `bot_settings.py`, you can customize:
    - Number of categories and products displayed per row.
    - All text messages. 🖊️
    - Primary and secondary languages.
    - Inline button text and callback data.
    - Payment link time limits. ⏳

### Django Backend 📚

- **Database Models**:
  - `UserData`: Manages user account information. By default, the language is set to English (`en`). If your primary language isn’t English, update this in `bot_settings.py`.
  - `Transaction`: Tracks payment transactions. 📋
  - `Category`, `Product`, `ProductDetail`: Manages products and their details. 🛠️
  - `ProductDetail`: The field detail that contain product info is encrypted 🔒 by ([django-encrypted-json-fields](https://pypi.org/project/django-encrypted-json-fields/))

---

## Installation ⚙️

### Prerequisites 🔎

1. Python 3.8 or higher 💾
2. Django (latest version recommended) ⬆️
3. PostgreSQL or any preferred database system configured in Django ([Learn More](https://docs.djangoproject.com/en/5.1/ref/databases/))
4. Required libraries: `python-telegram-bot`, `asgiref`, `python-decouple`, etc.
5. Dependencies are listed in `req.txt`

### Setup Instructions 🔧

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/RezaTaheri01/telegram-store-bot.git
   ```
   ```bash
   cd telegram-store-bot/telegram_store
   ```

2. **Install Dependencies**([virtual environment](https://realpython.com/python-virtual-environments-a-primer/#create-it) recommended):
   ```bash
   pip install -r req.txt
   ```

   
3. **Configure the `.env` File**:  
   Create a `.env` file in the project root and populate it with the following sample values:  
   ```env
   TOKEN=your-telegram-api-token   
   SECRET_KEY=django-insecure-$kp!7e*2sv#%i%=qq(-#pspemkli#ruf_5i04(2q+eeoae_+2h
   # Encrypting detail field with this key
   ENCRYPTION_KEYS=6-QgONW6TUl5rt4Xq8u-wBwPcb15sIYS2CN6d69zueM=  
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
   PAYMENT_DOMAIN=http://127.0.0.1:8000
   ```

4. **Migrate the Database** and  **Create Super User**:
   ```bash
   python manage.py makemigrations users payment products
   ```
   ```bash
   python manage.py migrate
   ```

   ```bash
   python manage.py createsuperuser
   ```
   

5. **Run the Django Development Server**:
   ```bash
   python manage.py runserver
   ```

6. **Run the Telegram Bot**:
   ```bash
   python bot.py
   ```

---

## Code Overview 🛠️

### Telegram Bot 📲

#### Key Features

- **Core Functions**:
  - `start_menu`: Displays the main menu. 🌐
  - `change_language`: Allows users to change their language and updates the `UserData` language field. 🌎
  - `check_create_account`: Automatically creates user accounts if they don’t exist. 🔧
  - `user_balance`: Fetches and displays the user’s balance. 💳
  - `deposit_money`: Initiates the deposit process and generates payment links. 💵
  - `charge_account`: Updates the user’s balance upon successful payment. ✔️
  - `get_name`: Retrieves names based on user language. 🌐
  - `product_categories`: Dynamically displays product categories. 🛒
  - `products`: Lists products under a selected category. 🍾
  - `product_payment_detail`: Displays payment details for a product. 💸
  - `payment`: Handles product purchases and balance deductions. 💰
  - `get_user_language`: Retrieves the user’s language from a language cache or the database. 🌐

#### Conversation States

- `ENTER_AMOUNT`: Captures the deposit amount entered by the user. 💵

#### Error Handling 🛠️

- Logs all errors to `bot_logs.log`.
- Notifies users of issues without disrupting the bot experience. ⚠️

---

### Payment Link Workflow 🔗

- **Link Format**:
  ```
  PAYMENT_URL + /payment/confirm/?chat_id={chat_id}&user_id={user_id}&amount={amount}&bot_link={bot_link}&transaction={transaction}
  ```
- Redirects users to a Django view for payment processing.

---

## Usage 🚀

1. **Start the Bot**:
   - Send `/start` to the bot. 📢
   - Explore options like **My Account**, **My Balance**, **Deposit**, or **Product Categories**.

2. **Deposit Money**:
   - Select the **Deposit** option from the menu. 💵
   - Enter the desired amount.
   - Click the payment link to complete the transaction. ✔️
   - Verify the updated balance in your account. 💳

3. **Browse Products**:
   - Select **Product Categories** from the menu. 🛒
   - Choose a category and view available products. 🍾
   - Purchase a product using your balance. 💰

---

## Logs 🔍

- All errors are logged in `bot_logs.log` with detailed messages. 📄

---

## Notes 📊

- Ensure the Django server is running for smooth payment processing. ⚙️
- Update the `PAYMENT_URL`, `ALLOWED_HOSTS` in the .env to match your server’s address when deploying. 🔗

---

## License 🔒

This project is licensed under the MIT License. See the [`LICENSE`](https://github.com/RezaTaheri01/telegram-store-bot/blob/main/LICENSE) file for more details. 🔖
