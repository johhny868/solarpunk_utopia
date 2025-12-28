"""Cryptography module for Solarpunk mesh network

Real encryption using industry-standard primitives:
- NaCl (libsodium) for message encryption
- AES-256-GCM for seed phrase encryption
- Scrypt for password-based key derivation
- Secure memory wiping for key destruction
"""

from .encryption import (
    encrypt_message,
    decrypt_message,
    encrypt_seed_phrase,
    decrypt_seed_phrase,
    secure_wipe_key,
    generate_x25519_keypair,
)

__all__ = [
    'encrypt_message',
    'decrypt_message',
    'encrypt_seed_phrase',
    'decrypt_seed_phrase',
    'secure_wipe_key',
    'generate_x25519_keypair',
]
