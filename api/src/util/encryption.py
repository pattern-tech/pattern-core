import os
import base64
import hashlib

from cryptography.fernet import Fernet


def generate_key(password: str) -> bytes:
    """
    Derive a key from the password.
    """
    # Hash the password to ensure it has the appropriate length
    password_bytes = password.encode('utf-8')
    hashed_password = hashlib.sha256(password_bytes).digest()
    # Use the hashed password as a key and encode it for Fernet
    return base64.urlsafe_b64encode(hashed_password)


def encrypt_message(message: str, password: str) -> str:
    """
    Encrypt a message using the password.
    """
    key = generate_key(password)
    fernet = Fernet(key)
    encrypted_message = fernet.encrypt(message.encode('utf-8'))
    return encrypted_message.decode('utf-8')


def decrypt_message(message: str, password: str) -> str:
    """
    Decrypt an encrypted message using the password.
    """
    key = generate_key(password)
    fernet = Fernet(key)
    decrypted_message = fernet.decrypt(message.encode('utf-8'))
    return decrypted_message.decode('utf-8')


# Example usage
if __name__ == "__main__":
    password = os.getenv("SECRET_KEY")
    message = "This is a secret message."

    # Encrypt the message
    encrypted = encrypt_message(message, password)
    print(f"Encrypted message: {encrypted}")

    # Decrypt the message
    decrypted = decrypt_message(encrypted, password)
    print(f"Decrypted message: {decrypted}")
