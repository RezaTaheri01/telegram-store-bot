# Telegram Store Bot 🛒

## Overview 📌

This is a Telegram bot for managing a store where users can view products, make purchases using TON cryptocurrency, and manage their accounts. It integrates with Django ORM for database operations, supports multi-language, and tracks transactions securely.

## Features ✨

* User registration and account management 👤
* Product browsing by categories 🏷️
* Purchase products using TON cryptocurrency 💰
* Generate TON payment links 🔗
* Track user transactions and purchase history 📝
* Background tasks to fetch TON prices and process transactions ⏱️
* Multi-language support 🌐
* Timezone handling ⏰
* Retry failed transactions 🔄

## Setup & Installation 🛠️

1. Clone the repository:

```bash
git clone --branch TON-payment https://github.com/RezaTaheri01/telegram-store-bot.git
cd telegram-store-bot/telegram_store
```

2. Install dependencies:

```bash
pip install -r req.txt
```

3. Set environment variables in `.env` or `bot_settings.py`:

```env
# Bot Token(@BotFather)
TOKEN=your-telegram-api-token   
BOT_LINK=https://t.me/giftShop2025Bot

SECRET_KEY=CHANGE_ME_IN_PRODUCTION

# Set to False when deploying!
DEBUG=True   

# No slash at the end
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
ADMIN_URL=adminadmin

# Local Storage Image Domain(Site Domain)
# SITE_DOMAIN=https://

# Database
#DB_ENGINE=postgresql
#DB_NAME=mydb
#DB_USER=postgres
#DB_PASS=secret123
#DB_HOST=localhost
#DB_PORT=5432
```

4. Configure Django settings and run migrations:

```bash
python manage.py makemigrations users payment products
python manage.py migrate
python manage.py createsuperuser
```

5. Start Django Backend:

```bash
python manage.py runserver
```

6. Move to admin and create a bot settings instance and fill all fields

7. Start the bot:

```bash
python bot.py
```

## Bot Commands 📋

* `/start` - Start the bot and display main menu 🚀
* `/menu` - Show main menu 🏠
* `/balance` - Check user balance 💵
* `/pay` - Generate TON payment link 🔗
* `Update Settings` - Refresh bot settings ⚙️

## User Flow 🔄

1. Users start the bot and create an account.
2. Users browse product categories and select products.
3. TON payment links are generated for users.
4. Users can view transactions and purchase history.
5. Background jobs handle TON price updates, transaction polling, and failed transaction retries.

## Caching & Optimization ⚡

* **TTLCache** for settings, language, timezone, and TON price.
* **LRUCache** for recent transaction hashes.
* Async and sync_to_async functions for Django ORM to support non-blocking operations.

## Error Handling 🛡️

* Rotating log files (5 MB each, 5 backups) for errors and warnings.
* Global error handler for bot exceptions.
* Retry mechanism for sending messages and failed transactions.

## Notes & TODO 📌

* Handle high traffic and large number of transactions.
* Ensure atomic updates to avoid double-spending.
* Retry failed transactions automatically.
* Optionally move background tasks to Django Celery for better scaling.

## Tech Stack 🖥️

* Python 3.11+
* Django ORM
* `python-telegram-bot` v20+
* Aiohttp for async HTTP requests
* Cachetools for caching
* Timezone handling with `pytz` and `timezonefinder` (Need to be enabled in bot.py main function)
