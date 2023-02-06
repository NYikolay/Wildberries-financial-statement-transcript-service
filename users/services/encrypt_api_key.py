from cryptography.fernet import Fernet

from config.settings.base import SECRET_CODE


def get_encrypted_key(api_key: str) -> str:
    fernet_obj = Fernet(SECRET_CODE.encode())

    return fernet_obj.encrypt(api_key.encode()).decode()
