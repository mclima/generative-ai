"""
Encryption utilities for sensitive data at rest.

Uses Fernet (symmetric encryption) from cryptography library for encrypting
sensitive data like API keys and other secrets stored in the database.

Note: Passwords are hashed using bcrypt, not encrypted.
"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import os
from typing import Optional

from app.config import get_settings
from app.logging_config import get_logger

settings = get_settings()
logger = get_logger(__name__)


class EncryptionService:
    """
    Service for encrypting and decrypting sensitive data at rest.
    
    Uses Fernet symmetric encryption with a key derived from the JWT secret.
    This ensures that encrypted data can only be decrypted with the correct key.
    """
    
    def __init__(self, secret_key: Optional[str] = None):
        """
        Initialize encryption service.
        
        Args:
            secret_key: Secret key for encryption (defaults to JWT secret from settings)
        """
        self.secret_key = secret_key or settings.jwt_secret_key
        self._fernet = self._create_fernet()
    
    def _create_fernet(self) -> Fernet:
        """
        Create Fernet instance with derived key.
        
        Uses PBKDF2 to derive a 32-byte key from the secret key.
        """
        # Use a fixed salt for key derivation (in production, consider using a per-installation salt)
        salt = b'us-stock-assistant-encryption-salt'
        
        # Derive a 32-byte key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(self.secret_key.encode()))
        return Fernet(key)
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext string.
        
        Args:
            plaintext: String to encrypt
            
        Returns:
            Base64-encoded encrypted string
            
        Raises:
            ValueError: If plaintext is empty
        """
        if not plaintext:
            raise ValueError("Cannot encrypt empty string")
        
        try:
            encrypted_bytes = self._fernet.encrypt(plaintext.encode())
            return encrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Encryption failed: {str(e)}")
            raise ValueError("Encryption failed")
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt ciphertext string.
        
        Args:
            ciphertext: Base64-encoded encrypted string
            
        Returns:
            Decrypted plaintext string
            
        Raises:
            ValueError: If decryption fails
        """
        if not ciphertext:
            raise ValueError("Cannot decrypt empty string")
        
        try:
            decrypted_bytes = self._fernet.decrypt(ciphertext.encode())
            return decrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {str(e)}")
            raise ValueError("Decryption failed - invalid ciphertext or key")
    
    def encrypt_dict(self, data: dict, fields_to_encrypt: list) -> dict:
        """
        Encrypt specific fields in a dictionary.
        
        Args:
            data: Dictionary containing data
            fields_to_encrypt: List of field names to encrypt
            
        Returns:
            Dictionary with specified fields encrypted
        """
        encrypted_data = data.copy()
        
        for field in fields_to_encrypt:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[field] = self.encrypt(str(encrypted_data[field]))
        
        return encrypted_data
    
    def decrypt_dict(self, data: dict, fields_to_decrypt: list) -> dict:
        """
        Decrypt specific fields in a dictionary.
        
        Args:
            data: Dictionary containing encrypted data
            fields_to_decrypt: List of field names to decrypt
            
        Returns:
            Dictionary with specified fields decrypted
        """
        decrypted_data = data.copy()
        
        for field in fields_to_decrypt:
            if field in decrypted_data and decrypted_data[field]:
                try:
                    decrypted_data[field] = self.decrypt(decrypted_data[field])
                except ValueError:
                    # If decryption fails, log warning and keep encrypted value
                    logger.warning(f"Failed to decrypt field: {field}")
        
        return decrypted_data


# Global encryption service instance
_encryption_service: Optional[EncryptionService] = None


def get_encryption_service() -> EncryptionService:
    """
    Get global encryption service instance.
    
    Returns:
        EncryptionService instance
    """
    global _encryption_service
    
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    
    return _encryption_service


def encrypt_api_key(api_key: str) -> str:
    """
    Encrypt an API key for storage.
    
    Args:
        api_key: API key to encrypt
        
    Returns:
        Encrypted API key
    """
    service = get_encryption_service()
    return service.encrypt(api_key)


def decrypt_api_key(encrypted_key: str) -> str:
    """
    Decrypt an API key from storage.
    
    Args:
        encrypted_key: Encrypted API key
        
    Returns:
        Decrypted API key
    """
    service = get_encryption_service()
    return service.decrypt(encrypted_key)
