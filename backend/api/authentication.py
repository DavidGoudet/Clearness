import jwt
import requests
from django.conf import settings
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token


def verify_google_token(token: str) -> dict:
    """Verify a Google OAuth2 ID token and extract user information.

    Args:
        token: The Google ID token string to verify.

    Returns:
        A dictionary with keys: email, name, provider_id.

    Raises:
        ValueError: If the token is invalid, expired, or has wrong audience.
    """
    idinfo = id_token.verify_oauth2_token(
        token,
        google_requests.Request(),
        audience=settings.GOOGLE_CLIENT_ID,
    )
    return {
        "email": idinfo["email"],
        "name": idinfo.get("name", ""),
        "provider_id": idinfo["sub"],
    }


APPLE_PUBLIC_KEYS_URL = "https://appleid.apple.com/auth/keys"


def verify_apple_token(identity_token: str) -> dict:
    """Verify an Apple identity token using Apple's public keys (JWKS).

    Args:
        identity_token: The Apple identity token (JWT) to verify.

    Returns:
        A dictionary with keys: email, provider_id.

    Raises:
        ValueError: If the token is invalid, expired, has wrong audience/issuer,
            or no matching key is found.
    """
    try:
        apple_keys = requests.get(APPLE_PUBLIC_KEYS_URL, timeout=10).json()["keys"]
    except (requests.RequestException, KeyError) as exc:
        raise ValueError("Failed to fetch Apple public keys") from exc

    header = jwt.get_unverified_header(identity_token)
    kid = header.get("kid")
    if not kid:
        raise ValueError("Apple token missing kid header")

    matching_key = None
    for k in apple_keys:
        if k.get("kid") == kid:
            matching_key = k
            break
    if matching_key is None:
        raise ValueError("No matching Apple public key found")

    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(matching_key)
    payload = jwt.decode(
        identity_token,
        public_key,
        algorithms=["RS256"],
        audience=settings.APPLE_CLIENT_ID,
        issuer="https://appleid.apple.com",
    )
    return {
        "email": payload.get("email", ""),
        "provider_id": payload["sub"],
    }
