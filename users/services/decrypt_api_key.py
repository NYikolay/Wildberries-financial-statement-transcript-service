from config.settings.base import SECRET_CODE
from cryptography.fernet import Fernet


def get_decrypted_key(api_key: str) -> str:
    fernet_obj = Fernet(SECRET_CODE.encode())

    return fernet_obj.decrypt(api_key.encode()).decode()
