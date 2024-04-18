# Python Warehouse bot

![](https://img.shields.io/badge/python-v3.10-informational) ![](https://img.shields.io/badge/aiogram-v2.25.1-informational)


This is bot for warehouse accounting

## Running Locally

Brief example with venv
```cmd
git clone https://github.com/valentinkelbakh/WarehouseBot.git
cd WarehouseBot
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
```
To run the bot:
```
python -m app
```

If you run on linux, Bot requires font DejaVu, can be installed with similar command:
```bash
sudo apt-get install ttf-dejavu
```

Create .env based on .env.example.

App can use ngrok for webhook
Webhook host will only be used only if SERVERLESS=True and NGROK=False.

Database is REST API Service, specifically this:
[WarehouseDatabase](https://github.com/valentinkelbakh/WarehouseDatabase "WarehouseDatabase")

## Features


The bot supports multiple users, authenticated via phone numbers. Key entities include User, Role, Department, Category, Product, Receipt, and Inventory.

Users are assigned roles determining their access privileges. Products are associated with departments and may belong to categories (with each product tied to one category).

Adding, moving, or removing products involves creating Receipts, specifying product details and their source/destination. The Inventory feature enables viewing departmental inventory in real-time or at specified dates.

Entities can be added, modified, or deleted, except for Inventory, which is read-only. Deletion of entities is allowed only if entity is not in use.

At the moment, bot only works in russian language.
