# Proposal: Fix Real Encryption - Replace Placeholders with Actual Crypto

**Submitted By:** Gap Analysis Agent
**Date:** 2025-12-19
**Status:** ✅ IMPLEMENTED
**Gaps Addressed:** GAP-112, GAP-114, GAP-116, GAP-119
**Priority:** P0 - Before Workshop
**Implemented:** 2025-12-19

## Problem Statement

Multiple "implemented" features use placeholder cryptography:

1. **GAP-116**: Mesh messages use Base64 encoding labeled as "encryption"
2. **GAP-112**: Panic service seed phrase "encryption" is just string formatting
3. **GAP-114**: Panic wipe claims to delete keys but doesn't
4. **GAP-119**: Admin endpoints have no authentication

These are CRITICAL security failures that would expose users to surveillance and harm.

## Current State (Broken)

### Mesh Messaging (`app/api/messages.py:92-93`)
```python
# TODO: Replace with actual X25519 encryption
encrypted_content = base64.b64encode(request.content.encode()).decode()
```
**Risk:** Messages readable by any relay node.

### Panic Seed Phrase (`app/services/panic_service.py:354`)
```python
# TODO: Implement proper encryption
return f"ENCRYPTED[{seed_phrase}]"  # NOT ENCRYPTED!
```
**Risk:** Seed phrases stored in plaintext.

### Panic Wipe (`app/services/panic_service.py:249`)
```python
# TODO: Implement key storage wipe
wiped_types.append("private_keys")  # Claims to wipe but doesn't!
```
**Risk:** Keys recoverable after "wipe".

### Admin Endpoints (`app/api/sanctuary.py:224`)
```python
# TODO: Add authentication - this should only be callable by background worker
```
**Risk:** Anyone can purge sanctuary data.

## Proposed Solution

### 1. Real Message Encryption (X25519 + XSalsa20-Poly1305)

```python
from nacl.public import PrivateKey, PublicKey, Box
from nacl.utils import random

def encrypt_message(plaintext: str, recipient_pubkey: bytes, sender_privkey: bytes) -> bytes:
    """Encrypt message using NaCl box (X25519 + XSalsa20-Poly1305)"""
    sender_key = PrivateKey(sender_privkey)
    recipient_key = PublicKey(recipient_pubkey)
    box = Box(sender_key, recipient_key)
    nonce = random(Box.NONCE_SIZE)
    return box.encrypt(plaintext.encode(), nonce)

def decrypt_message(ciphertext: bytes, sender_pubkey: bytes, recipient_privkey: bytes) -> str:
    """Decrypt message"""
    recipient_key = PrivateKey(recipient_privkey)
    sender_key = PublicKey(sender_pubkey)
    box = Box(recipient_key, sender_key)
    return box.decrypt(ciphertext).decode()
```

### 2. Real Seed Phrase Encryption (AES-256-GCM)

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

def encrypt_seed_phrase(seed_phrase: str, password: str) -> bytes:
    """Encrypt seed phrase with password-derived key"""
    # Derive key from password using Argon2
    salt = os.urandom(16)
    key = derive_key_argon2(password, salt)

    # Encrypt with AES-256-GCM
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, seed_phrase.encode(), None)

    return salt + nonce + ciphertext
```

### 3. Secure Key Destruction

```python
import ctypes

def secure_wipe_key(key_bytes: bytearray):
    """Securely wipe key from memory"""
    # Overwrite with zeros
    ctypes.memset(ctypes.addressof(ctypes.c_char.from_buffer(key_bytes)), 0, len(key_bytes))

    # Overwrite with random
    random_bytes = os.urandom(len(key_bytes))
    for i in range(len(key_bytes)):
        key_bytes[i] = random_bytes[i]

    # Final zero
    ctypes.memset(ctypes.addressof(ctypes.c_char.from_buffer(key_bytes)), 0, len(key_bytes))

async def panic_wipe_keys():
    """Actually wipe private keys"""
    key_store = get_key_store()

    # Get key as mutable bytearray
    private_key = bytearray(key_store.get_private_key())

    # Secure wipe
    secure_wipe_key(private_key)

    # Delete from storage
    key_store.delete_all_keys()

    # Force filesystem sync
    os.sync()
```

### 4. Admin Endpoint Authentication

```python
from app.auth.middleware import require_admin_key

@router.post("/admin/purge")
@require_admin_key  # Requires ADMIN_API_KEY environment variable
async def admin_purge_expired():
    """Purge expired data - admin only"""
    ...
```

## Requirements

### SHALL Requirements
- SHALL use NaCl/libsodium for message encryption (X25519 + XSalsa20-Poly1305)
- SHALL use AES-256-GCM for seed phrase encryption
- SHALL use Argon2 for password-based key derivation
- SHALL securely overwrite key material before deletion
- SHALL require authentication for all admin endpoints
- SHALL NOT use Base64 as "encryption"
- SHALL NOT store plaintext cryptographic material

### MUST Requirements
- MUST pass cryptographic audit before workshop
- MUST work on old Android phones (ARM support for libsodium)

## Testing

```python
def test_message_encryption_is_real():
    """Verify messages are actually encrypted, not Base64"""
    plaintext = "secret message"
    encrypted = encrypt_message(plaintext, recipient_pub, sender_priv)

    # Should NOT be decodable as Base64 text
    try:
        decoded = base64.b64decode(encrypted).decode()
        assert decoded != plaintext, "Message is just Base64!"
    except:
        pass  # Good - not Base64

    # Should only decrypt with correct keys
    decrypted = decrypt_message(encrypted, sender_pub, recipient_priv)
    assert decrypted == plaintext

def test_panic_wipe_destroys_keys():
    """Verify keys are actually wiped"""
    key_store = create_test_key_store()
    key_store.store_key(b"secret_key_material")

    await panic_wipe_keys()

    # Key should not be recoverable
    assert key_store.get_private_key() is None
```

## Dependencies

- `pynacl` >= 1.5.0 (NaCl bindings)
- `cryptography` >= 41.0.0 (AES-GCM, Argon2)

## Files to Modify

1. `app/api/messages.py` - Replace Base64 with NaCl
2. `app/services/panic_service.py` - Real encryption, real wipe
3. `app/api/sanctuary.py` - Add admin auth
4. `app/api/rapid_response.py` - Add admin auth
5. `app/auth/middleware.py` - Add `require_admin_key` decorator

## Effort Estimate

- 4-6 hours implementation
- 2 hours testing
- 1 hour documentation

## Success Criteria

- [ ] All messages encrypted with X25519
- [ ] Seed phrases encrypted with AES-256-GCM
- [ ] Panic wipe securely destroys keys
- [ ] Admin endpoints require authentication
- [ ] No Base64 "encryption" anywhere in codebase
- [ ] All crypto tests passing
