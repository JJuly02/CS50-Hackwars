import os
import re
from cs50 import SQL
from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import datetime

from helper import login_required

app = Flask(__name__)

# Konfiguracja bazy danych
dbimperial = SQL("sqlite:///imperialnet.db")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    #TODO Logika logowania
    return render_template("index.html")

@app.route("/score")
@login_required
def score():
    #TODO Logika wyświetlania punktacji
    render_template("index.html")

@app.route("/imperialnet")
def imperialnetindex():
    return render_template("imperialnetindex.html")

@app.route("/imperialnet/<username>")
def imperialnet(username):
     # Prepare the username for a case-insensitive match
    username_formatted = username.replace("-", " ").title()

    # Retrieve user details based on the username
    user = dbimperial.execute("SELECT * FROM Users WHERE LOWER(name) = LOWER(?)", username_formatted)
    if not user:
        return "User not found", 404

    user_id = user[0]['id']

    # Retrieve job descriptions for the user
    jobs = dbimperial.execute("SELECT * FROM JobDescriptions WHERE user_id = ?", user_id)

    # Retrieve skills for the user
    skills = dbimperial.execute("SELECT * FROM Skills WHERE user_id = ?", user_id)

    # Render a template with user details, jobs, and skills
    return render_template("profile.html", user=user[0], jobs=jobs, skills=skills)

    # Ai helped with the sql to speed up the procces, also it helped me with the descriptions to write faster

@app.route("/imperialnet/login")
def imperialnet_login():
    return render_template("imperiallogin.html")

@app.route("/imperialnet/register")
def imperialnet_register():
    return render_template("imperialregister.html")

if __name__ == "__main__":
    app.run(debug=True)

