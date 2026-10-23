from functools import wraps

import jwt
from flask import g, jsonify, redirect, request, url_for
from jwt_signing import PUBLIC_KEY


def get_token():
    header = request.headers.get("Authorization", "")

    if header.startswith("Bearer "):
        return header[len("Bearer "):].strip()

    return request.cookies.get("access_token")


def token_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = get_token()

        if not token:
            if request.path.startswith("/api/") or request.is_json:
                return jsonify(error="Authentication required"), 401
            return redirect(url_for("login"))

        try:
            claims = jwt.decode(
                token,
                PUBLIC_KEY,
                algorithms=["RS256"],
                options={"require": ["sub", "role", "exp"]},
            )
        except jwt.ExpiredSignatureError:
            if request.path.startswith("/api/"):
                return jsonify(error="Token expired"), 401
            return redirect(url_for("login", error="Your session expired"))
        except jwt.InvalidTokenError:
            if request.path.startswith("/api/"):
                return jsonify(error="Invalid token"), 401
            return redirect(url_for("login", error="Please sign in again"))

        g.jwt_claims = claims
        return func(*args, **kwargs)

    return wrapper