import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

BASE_DIR = Path(__file__).resolve().parent
PRIVATE_KEY_PATH = BASE_DIR / "lab_jwt_private.pem"

def load_or_create_signing_key():
    if PRIVATE_KEY_PATH.exists():
        os.chmod(PRIVATE_KEY_PATH, 0o600)
        return serialization.load_pem_private_key(
            PRIVATE_KEY_PATH.read_bytes(),
            password=None,
        )

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    PRIVATE_KEY_PATH.write_bytes(pem)
    os.chmod(PRIVATE_KEY_PATH, 0o600)
    return private_key


PRIVATE_KEY = load_or_create_signing_key()

PUBLIC_KEY = PRIVATE_KEY.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
).decode("utf-8")


def issue_token(user):
    now = datetime.now(timezone.utc)
    return jwt.encode({
        "sub": user["username"],
        "role": user["role"],
        "iat": now,
        "exp": now + timedelta(hours=1),
    }, PRIVATE_KEY, algorithm="RS256")