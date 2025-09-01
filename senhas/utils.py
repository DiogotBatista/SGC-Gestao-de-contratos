# senhas/utils.py
from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings

def get_fernet():
    key = (settings.DJANGO_PASSWORDS_KEY or "").strip()
    if not key:
        raise RuntimeError("DJANGO_PASSWORDS_KEY não definida no .env")
    try:
        return Fernet(key.encode())
    except Exception as e:
        raise RuntimeError(f"DJANGO_PASSWORDS_KEY inválida: {e}")

def encrypt_str(plain: str) -> bytes:
    return get_fernet().encrypt(plain.encode('utf-8'))

def decrypt_bytes(token: bytes) -> str:
    try:
        return get_fernet().decrypt(token).decode('utf-8')
    except InvalidToken:
        return "[ERRO: token inválido]"
