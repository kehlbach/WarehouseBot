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

## Demo

Every function represented by the buttons in the images is fully functional

### Menu

![menu](https://github.com/valentinkelbakh/WarehouseBot/assets/114210745/1ecc12f1-2788-4c9e-8434-27082ee014fb)

### Role

![role1](https://github.com/valentinkelbakh/WarehouseBot/assets/114210745/f28e6785-ee5f-4146-830f-b6ee69475ed6)

![role2](https://github.com/valentinkelbakh/WarehouseBot/assets/114210745/babdc974-15ac-47c9-9b7e-41711e917b4f)

### Inventory

![inventory1](https://github.com/valentinkelbakh/WarehouseBot/assets/114210745/e38ca2d9-3f2f-4be2-9959-b21f98a33a32)

![inventory2](https://github.com/valentinkelbakh/WarehouseBot/assets/114210745/562cb119-575a-4b22-a7b9-17ce45cfc77a)

### Receipt

![receipt1](https://github.com/valentinkelbakh/WarehouseBot/assets/114210745/b312217e-c5f1-4dd7-93a7-1cb1dbd462a9)

![receipt2](https://github.com/valentinkelbakh/WarehouseBot/assets/114210745/494204c4-549b-45fb-8695-85ab8615a037)

![receipt3](https://github.com/valentinkelbakh/WarehouseBot/assets/114210745/6c65a47f-372f-473e-8e31-56365e3f4459)

### Product

![product1](https://github.com/valentinkelbakh/WarehouseBot/assets/114210745/bbb18dbd-1c7f-4ef8-a6cc-8f3ab58beb8a)

![product2](https://github.com/valentinkelbakh/WarehouseBot/assets/114210745/d2f60c64-2ab0-4984-a646-5bf3bc4cd845)

### Category

![category1](https://github.com/valentinkelbakh/WarehouseBot/assets/114210745/cda4ac96-8c00-4aa6-86a1-5903b1a56e9a)

![category2](https://github.com/valentinkelbakh/WarehouseBot/assets/114210745/308f9eee-41cb-4bb7-8922-3fc1e05beb74)

### Department

![department1](https://github.com/valentinkelbakh/WarehouseBot/assets/114210745/75ef9b51-28cd-47e9-876b-1f09b2db33a7)

![department2](https://github.com/valentinkelbakh/WarehouseBot/assets/114210745/a1c00bf0-bde7-443d-ae96-9669755cff55)

