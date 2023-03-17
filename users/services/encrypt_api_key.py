from cryptography.fernet import Fernet

from config.settings.base import SECRET_CODE


def get_encrypted_key(api_key: str) -> str:
    """
    The function encrypts the string based on the secret word.
    :param api_key: The api_key field of the WBApiKey model
    :return: Returns the encrypted string
    """
    fernet_obj = Fernet(SECRET_CODE.encode())

    return fernet_obj.encrypt(api_key.encode()).decode()
