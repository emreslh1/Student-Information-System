"""Password hashing and verification utilities."""
import hashlib
import secrets
import base64


def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """
    Hash a password with a salt using PBKDF2.
    
    Args:
        password: The plain text password to hash
        salt: Optional salt (hex string). If None, generates a new salt.
        
    Returns:
        Tuple of (password_hash, salt) both as hex strings
    """
    if salt is None:
        salt = secrets.token_hex(32)
    
    # Use PBKDF2 with SHA-256
    password_bytes = password.encode('utf-8')
    salt_bytes = bytes.fromhex(salt)
    
    hash_bytes = hashlib.pbkdf2_hmac(
        'sha256',
        password_bytes,
        salt_bytes,
        100000  # 100,000 iterations
    )
    
    password_hash = hash_bytes.hex()
    return password_hash, salt


def verify_password(password: str, password_hash: str, salt: str) -> bool:
    """
    Verify a password against a stored hash.
    
    Args:
        password: The plain text password to verify
        password_hash: The stored password hash (hex string)
        salt: The stored salt (hex string)
        
    Returns:
        True if the password matches, False otherwise
    """
    computed_hash, _ = hash_password(password, salt)
    return secrets.compare_digest(computed_hash, password_hash)
