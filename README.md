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

2. Install dependencies(venv recommended):

```bash
pip install -r req.txt
```

3. Collect static files:

```bash
python manage.py collectstatic --noinput
```

4. Set environment variables in `.env` or `bot_settings.py`:

```env
# Bot Token(@BotFather)
TOKEN=your-telegram-api-token   
BOT_LINK=https://t.me/giftShop2025Bot

# Command to clear BotSetting cache via bot(Change it on deployment and keep it private)
UPDATE_SETTING_COMMAND=update

# Django secret key
SECRET_KEY=CHANGE_ME_IN_PRODUCTION

# Set to False when deploying!
DEBUG=True   

# No slash at the end
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com,www.your-domain.com
ADMIN_URL=adminadmin

# No slash at the end
# Local Storage Image Domain(Site Domain) 
# SITE_DOMAIN=https://your-domain.com

# Database
#DB_ENGINE=postgresql
#DB_NAME=mydb
#DB_USER=postgres
#DB_PASS=secret123
#DB_HOST=localhost
#DB_PORT=5432
```

5. Configure Django settings and run migrations:

```bash
python manage.py makemigrations users payment products
python manage.py migrate
python manage.py createsuperuser
```

6. Start Django Backend:

```bash
python manage.py runserver
```

7. Open the Django admin panel and create a Bot Settings entry. Recommended values:

    • **Wallet Currency**  
    Use standard 3-letter uppercase currency codes like USD

    • **TON Price Delay (seconds):** 120  
    How often the bot refreshes the live TON price.

    • **TON Fetch Limit:** 500  
    Increase this if you have many active users or high transaction volume.

    • **TON Network Delay (seconds):** 10  
    Interval for checking new on-chain transactions. Reduce for faster detection.

    • **Failed Transactions Delay (seconds):** 240  
    These are already stored in the database, so checking less often is fine.

    • **Disable Product Images**  
    Turn this on for a cleaner UI and faster loading in Telegram.

    • **API Keys**  
    All required API keys for the bot are free to obtain.



8. Start the bot:

```bash
python bot.py
```

## Bot Commands 📋

* `/start` - Start the bot and display main menu 🚀
* `/menu` - Show main menu 🏠
* `/balance` - Check user balance 💵
* `/pay` - Generate TON payment link 🔗
* `/set_timezone` -  Change user timezone base on location 🗺️
* `Update Settings` - Refresh bot settings ⚙️

## User Flow 🔄

1. Users start the bot and create an account.
2. Users browse product categories and select products.
3. TON payment links are generated for users to charge their account.
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
* Optionally move background tasks to Django Celery for better scaling.

## Tech Stack 🖥️

* Python 3.11+
* Django ORM
* `python-telegram-bot` v20+
* Aiohttp for async HTTP requests
* Cachetools for caching
* Timezone handling with `pytz` and `timezonefinder` (Timezone need to be enabled in bot.py main function)
