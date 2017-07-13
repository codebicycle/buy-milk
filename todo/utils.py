import base64
from flask import redirect, request
from functools import wraps
import os


def https_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.scheme == 'http':
            https_url = request.url.replace('http', 'https', 1)
            return redirect(https_url)

        return f(*args, **kwargs)

    return decorated_function
