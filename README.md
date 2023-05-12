# Python Warehouse bot

![](https://img.shields.io/badge/python-v3.10-informational) ![](https://img.shields.io/badge/aiogram-v2.25.1-informational)


This is bot for warehouse accounting

## Running Locally
#### To be done later


```cmd
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python -m app
```
Also requires .env file like this:
```
SERVERLESS=True
NGROK=True
API_TOKEN=[YOUR API TOKEN]
DB_LOGIN=
DB_PASSWORD=
DB_API_URL=[URL]
ADMIN_NUMBER=
WEBHOOK_HOST=[URL]
WEBAPP_HOST=127.0.0.1
WEBAPP_PORT=5000
```
Webhook host will only be used only if SERVERLESS=True and NGROK=False.

Database is REST API Service, specifically this:
[WarehouseDatabase](https://github.com/valentinkelbakh/WarehouseDatabase "WarehouseDatabase")
