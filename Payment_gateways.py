import os
import requests

# ------------------ Chimoney Setup ------------------

CHIMONEY_API_KEY = os.getenv("CHIMONEY_API_KEY")
CHIMONEY_API_SECRET = os.getenv("CHIMONEY_API_SECRET")
CHIMONEY_BASE_URL = "https://api.chimoney.io/v1"  # Confirm latest from docs

CHIMONEY_HEADERS = {
    "x-api-key": CHIMONEY_API_KEY,
    "Authorization": f"Bearer {CHIMONEY_API_SECRET}",
    "Content-Type": "application/json"
}

def chimoney_get_balance(wallet_id):
    """
    Fetch balance from Chimoney wallet.
    """
    url = f"{CHIMONEY_BASE_URL}/wallets/{wallet_id}/balance"
    try:
        response = requests.get(url, headers=CHIMONEY_HEADERS)
        if response.ok:
            return response.json()
    except Exception as e:
        print(f"[Chimoney Balance Error]: {e}")
    return None

def chimoney_send_funds(wallet_id, amount, currency, recipient):
    """
    Send funds via Chimoney wallet.
    """
    url = f"{CHIMONEY_BASE_URL}/wallets/{wallet_id}/send"
    payload = {
        "amount": amount,
        "currency": currency,
        "recipient": recipient  # Could be phone/email/wallet_id
    }
    try:
        response = requests.post(url, json=payload, headers=CHIMONEY_HEADERS)
        if response.ok:
            return response.json()
    except Exception as e:
        print(f"[Chimoney Transfer Error]: {e}")
    return None

# ------------------ WalletsAfrica Setup ------------------

WALLETSAFRICA_API_KEY = os.getenv("WALLETSAFRICA_API_KEY")
WALLETSAFRICA_API_SECRET = os.getenv("WALLETSAFRICA_API_SECRET")
WALLETSAFRICA_BASE_URL = "https://api.wallets.africa/v1"  # Confirm from docs

WALLETSAFRICA_HEADERS = {
    "x-api-key": WALLETSAFRICA_API_KEY,
    "Authorization": f"Bearer {WALLETSAFRICA_API_SECRET}",
    "Content-Type": "application/json"
}

def walletsafrica_get_balance(account_id):
    """
    Fetch balance from WalletsAfrica account.
    """
    url = f"{WALLETSAFRICA_BASE_URL}/accounts/{account_id}/balance"
    try:
        response = requests.get(url, headers=WALLETSAFRICA_HEADERS)
        if response.ok:
            return response.json()
    except Exception as e:
        print(f"[WalletsAfrica Balance Error]: {e}")
    return None

def walletsafrica_send_funds(account_id, amount, currency, recipient_account):
    """
    Initiate transfer via WalletsAfrica account.
    """
    url = f"{WALLETSAFRICA_BASE_URL}/transfers"
    payload = {
        "account_id": account_id,
        "amount": amount,
        "currency": currency,
        "recipient_account": recipient_account
    }
    try:
        response = requests.post(url, json=payload, headers=WALLETSAFRICA_HEADERS)
        if response.ok:
            return response.json()
    except Exception as e:
        print(f"[WalletsAfrica Transfer Error]: {e}")
    return None
