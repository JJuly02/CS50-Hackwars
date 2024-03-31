from flask import redirect, render_template, session
from functools import wraps
from itertools import combinations
from werkzeug.security import check_password_hash, generate_password_hash


# lended this helper.py from cs50 flask
def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def login_requiredarch(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def apology(message, code=400):
    return render_template("rebel/apology.html", top=code, bottom=message), code

def detect_xss_payload(text):
    """
    Detects specific XSS payload patterns that include an alert function.
    """
    return "<script>alert(" in text

def hash_the_score(username, score):
    text = f"{username}{score}"

    return generate_password_hash(text, method='pbkdf2:sha256', salt_length=4)
