import base64
from flask import redirect, request
from functools import wraps
import os


def token_urlsafe(num_bytes=16):
    """Return a random URL-safe text string, in Base64 encoding.

    Source: Python 3.6 secrets.token_urlsafe()
    https://github.com/python/cpython/blob/master/Lib/secrets.py

    """
    token = os.urandom(num_bytes)
    return base64.urlsafe_b64encode(token).rstrip(b'=').decode('ascii')


def https_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.scheme == 'http':
            https_url = request.url.replace('http', 'https', 1)
            return redirect(https_url)

        return f(*args, **kwargs)

    return decorated_function
