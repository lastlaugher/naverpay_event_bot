from cryptography.fernet import Fernet

key = b'aqR62sFuSaXCQvpwZ4-NEMy_Sve86z9LWWSmKqa53zo='

def encrypt(message: str) -> bytes:
    return Fernet(key).encrypt(bytes(message, 'utf-8'))

def decrypt(token: bytes) -> str:
    return Fernet(key).decrypt(token).decode('utf-8')