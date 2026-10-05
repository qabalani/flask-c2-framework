import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def generate_key() -> str:
    return base64.b64encode(AESGCM.generate_key(bit_length=256)).decode()


def encrypt(key_b64: str, plaintext: bytes) -> str:
    key = base64.b64decode(key_b64)
    aes = AESGCM(key)
    nonce = os.urandom(12)
    ct = aes.encrypt(nonce, plaintext, None)
    return base64.b64encode(nonce + ct).decode()


def decrypt(key_b64: str, token_b64: str) -> bytes:
    key = base64.b64decode(key_b64)
    blob = base64.b64decode(token_b64)
    nonce, ct = blob[:12], blob[12:]
    return AESGCM(key).decrypt(nonce, ct, None)
