from config.settings.base import SECRET_CODE
from cryptography.fernet import Fernet


def get_decrypted_key(api_key: str) -> str:
    """
    The function decrypts the string based on the secret word
    :param api_key: The api_key field of the WBApiKey model
    :return: Returns the decrypted string
    """
    fernet_obj = Fernet(SECRET_CODE.encode())

    return fernet_obj.decrypt(api_key.encode()).decode()
