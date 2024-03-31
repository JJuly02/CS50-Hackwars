import os
import re
from cs50 import SQL
from flask import Flask, render_template, request, redirect, session, flash, url_for, jsonify
from flask_session import Session
import time
from werkzeug.security import check_password_hash, generate_password_hash

from helper import login_required, apology, detect_xss_payload, hash_the_score

# TODO SECURITY & WORKING CHECK

app = Flask(__name__)

# Class for holoadd as a backup
class Holoload:
    stage = 0

    @classmethod
    def update(cls, new_stage):
        cls.stage = new_stage

    @classmethod
    def get(cls):
        return cls.stage


# Session config
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Konfiguracja bazy danych
dbimperial = SQL("sqlite:///databases/imperialnet.db")  # imperial page
db = SQL("sqlite:///databases/users.db")  # user database
dbholocron1 = SQL("sqlite:///databases/hint.db")  # darkholocron
palpdb = SQL("sqlite:///databases/palps.db")  # palpatine page

# In-memory comments
comments = [
    {'author': 'Colonel Yularen', 'text': 'This page is an excellent resource for the Empire.'},
    {'author': 'Clone Trooper Fives', 'text': 'Affirmative, this page greatly aids our mission.'},
    {'author': 'Clone Trooper Echo', 'text': 'Impressive layout! Very informative.'}
]

# Functions to verificate login


def login_holo(n):
    user_id = session["user_id"]

    # Secure that user dont use BAC with stage = 0
    sec_quer = db.execute("SELECT holocronstage FROM users WHERE id = ?", (user_id))
    holostage = sec_quer[0]["holocronstage"]

    if holostage < n:
        return False


def login_archive(n):
    user_id = session["user_id"]

    sec_quer = db.execute("SELECT archivestage FROM users WHERE id = ?", (user_id,))
    archivestage = sec_quer[0]["archivestage"]
    print(archivestage)
    if archivestage < n:
        return False


@app.route("/")
@login_required
def index():
    return render_template("/rebel/index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Must provide password", 400)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hashpass"], request.form.get("password")
        ):
            return apology("Invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("/rebel/login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        password = request.form.get("password")
        repassword = request.form.get("confirmation")

        if not request.form.get("username"):
            return apology("Must provide username", 40)

        # Password confirmation
        if not password:
            return apology("Must provide password", 41)
        if len(password) < 8:
            return apology("Password to short, should have at least have 8 characters", 42)
        if not any(char.isupper() for char in password):
            return apology("Password must contain at least one uppercase letter", 43)
        if not any(char.isdigit() for char in password):
            return apology("Password must contain at least one number", 44)
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return apology("Password must contain at least one special character", 45)
        if not repassword:
            return apology("Must provide password confirmation", 46)
        if repassword != password:
            return apology("Password confirmation is not the same as password", 47)

        # Sumbit
        try:
            rows = db.execute(
                "INSERT INTO users (username, hashpass) VALUES (?, ?)", request.form.get(
                    "username"), generate_password_hash(password)
            )
        except:
            return apology("User arleady exist!", 48)

        return render_template("/rebel/register.html")

    else:
        return render_template("/rebel/register.html")


@app.route("/logout")
def logout():
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/score", methods=["GET", "POST"])
@login_required
def score():
    user_id = session["user_id"]
    is_flags = False

    if request.method == "POST":
        # Pobieranie flagi z formularza
        flag_input = request.form.get("flag")

        # Sprawdzanie, czy flaga już istnieje dla tego użytkownika
        existing_flag = db.execute("SELECT * FROM flags WHERE user_id = ? AND flag = ?", user_id=user_id, flag=flag_input)
        if existing_flag:
            flash("Flag already submitted.")
            return redirect("/score")

        # Pobieranie wszystkich zahashowanych flag z validflags
        valid_flags = db.execute("SELECT flag FROM validflags")

        # Sprawdzanie poprawności flagi
        flag_is_valid = False
        for valid_flag in valid_flags:
            if check_password_hash(valid_flag["flag"], flag_input):
                flag_is_valid = True
                break

        if not flag_is_valid:
            flash("Invalid flag.")
            return redirect("/score")

        # Dodanie flagi do bazy danych jako tekst jawny, ponieważ jest poprawna
        db.execute("INSERT INTO flags (user_id, flag) VALUES (:user_id, :flag)", user_id=user_id, flag=flag_input)
        flash("Flag submitted successfully.")

    # Pobieranie danych użytkownika i jego flag
    user_data = db.execute("SELECT username, holocronstage, archivestage FROM users WHERE id = :user_id", user_id=user_id)
    flags = db.execute("SELECT flag FROM flags WHERE user_id = :user_id", user_id=user_id)

    # Score based on flags
    flag_points = 0
    for flag in flags:
        flag_points += 1

    if user_data:
        # Ekstrakcja poszczególnych wyników do osobnych zmiennych
        holocronstage = user_data[0]['holocronstage']
        archscore = user_data[0]['archivestage']
        username = user_data[0]["username"]

        general_score = flag_points + int(holocronstage) + int(archscore)

        if flag_points > 8 and int(archscore) > 0:
            is_flags = True

        hashedscore = hash_the_score(username, general_score)

        # Przekazywanie każdego wyniku jako osobna zmienna do szablonu
        return render_template("rebel/score.html", holocronstage=holocronstage, archscore=archscore, username=username, flags=flags, flag_points=flag_points, general_score=general_score, is_flags=is_flags, hashedscore=hashedscore)
    else:
        # Obsługa przypadku, gdy nie znaleziono danych użytkownika
        return apology("Score data not found.", 404)


# Words "scraped" from imperialnet
scraped_keywords = [
    "SheevPalpatine", "SithMaster", "Order66Ruler", "TheSenate",
    "SupremeChancellor", "GalacticEmpire", "NabooSenator", "DarkSide", "DarkLord66-Ruler!"
]


@app.route("/ImperialWebscraper", methods=["GET", "POST"])
def ImperialWebscraper():
    return render_template("rebel/scraper.html", scraped_keywords=scraped_keywords)

@app.route("/BruteForce", methods=["GET", "POST"])
def bruteforce():
    user_id = session["user_id"]
    if request.method == 'POST':
        keyword1 = request.form.get("keyword1")
        keyword2 = request.form.get("keyword2")

        # Fetch the stored hashed keys for the user
        user_keys = palpdb.execute("SELECT key1, key2 FROM users WHERE id = ?", 1)
        if not user_keys:
            return redirect("/BruteForce/animation")  # Or handle the error as appropriate

        stored_hashed_key1 = user_keys[0]['key1']
        stored_hashed_key2 = user_keys[0]['key2']

        # Check if either combination of keyword inputs matches the stored hashes
        match1 = check_password_hash(stored_hashed_key1, keyword1) and check_password_hash(stored_hashed_key2, keyword2)
        match2 = check_password_hash(stored_hashed_key1, keyword2) and check_password_hash(stored_hashed_key2, keyword1)

        if match1 or match2:
            # Update the stage of dark archive in the database
            db.execute("UPDATE users SET archivestage = ? WHERE id = ?", 1, user_id)
            time.sleep(1)
            return redirect("/BruteForce/animation")
        else:
            return redirect("/BruteForce/animation")
    else:
        return render_template("rebel/bruteforce.html")

@app.route("/BruteForce/animation", methods=["GET"])
def video():
    user_id = session["user_id"]
    # Getting user darkarchive stage
    stage = db.execute("SELECT archivestage FROM users WHERE id = ?", (user_id,))
    darkarchivestage = stage[0]['archivestage']

    if darkarchivestage == 1:
        message = "Accessing Dark Archive..."
        success = True
    else:
        message = "Accessing Dark Archive..."
        success = False

    return render_template("rebel/brutevideo.html", message=message, success=success)

#------------Dark-Holocron-------------Vader-Page-----------
@app.route("/darkholocron", methods=['GET', 'POST'])
@login_required
def dark_holocron():
    sessuser_id = session["user_id"]
    message = ''

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Insecure SQL query that is vulnerable to SQL injection
        try:
            query = dbholocron1.execute(f"SELECT id, username FROM holocron WHERE username = '{username}' AND pass = '{password}'")
            user_id = query[0]["id"]
            user = query[0]["username"]
        except:
            message = f"Query executed: SELECT id FROM holocron WHERE username = '{username}' AND pass = '{password}'"
            return render_template("dark/mlogin.html", message=message)

        # Select holostage
        holo = db.execute("SELECT holocronstage FROM users WHERE id = ?", sessuser_id)
        holocronstage = holo[0]["holocronstage"]

        if user != "Admin1":
            if holocronstage == 0:
                db.execute("UPDATE users SET holocronstage = ? WHERE id = ?", 1, sessuser_id)
            Holoload.update(1)
            print(Holoload.get())
            return redirect(f"/darkholocron/{user}")

        elif user == "Admin1":
            db.execute("UPDATE users SET holocronstage = ? WHERE id = ?", 2, sessuser_id)
            Holoload.update(2)
            print(Holoload.get())
            return redirect(f"/darkholocron/Admin1")
    else:
        return render_template("dark/mlogin.html")

# Broken access control
@app.route("/darkholocron/<username>")
@login_required
def dark_holocron_holocron(username):
    user_id = session["user_id"]
    is_skywalker = False
    is_sith_lord = True

    # Secure that user dont use BAC with stage = 0
    sec_quer = db.execute("SELECT holocronstage FROM users WHERE id = ?", (user_id,))
    holostage = sec_quer[0]["holocronstage"]

    if holostage < 0:
        return apology("You have to login first!", 404)

    # Sprawdzenie, czy zalogowany użytkownik to Darth Vader lub Emperor Palpatine
    if username == "DarthVader":
        username_display = "Darth Vader"
        is_skywalker = True
    elif username == "EmperorPalpatine":
        username_display = "Emperor Palpatine"
    else:
        username_display = username.replace("-", " ").title()
        is_sith_lord = False

    return render_template("dark/holocron.html", username=username_display, is_sith_lord=is_sith_lord, is_skywalker=is_skywalker)


@app.route("/darkholocron/sith")
@login_required
def dark_holocron_sith():
    if login_holo(0) == False:
        return apology("You have to login first!", 404)

    return render_template("dark/sith.html")


@app.route("/darkholocron/skywalker")
@login_required
def dark_holocron_skywalker():
    if login_holo(0) == False:
        return apology("You have to login first!", 404)

    return render_template("dark/skywalker.html")

@app.route("/darkholocron/admin", methods=['GET', 'POST'])
@login_required
def dark_holocron_admin():
    user_id = session["user_id"]

    # Secure that user dont use BAC with stage = 2
    sec_quer = db.execute("SELECT holocronstage FROM users WHERE id = ?", user_id)
    holostage = sec_quer[0]["holocronstage"]

    if holostage < 1:
        return apology("You have to login first!", 404)

    # veryficate if user is on the apropriate stage if not give him point for broken access control
    message = ""
    if holostage == 1 and Holoload.get() != 2:
        message = "Broken access control - IMP-BROK3NKONTROL"
        new_holocronstage = 2
        db.execute("UPDATE users SET holocronstage = ? WHERE id = ?", new_holocronstage, user_id)
        return render_template("dark/admin.html", message=message, username="Admin1")
    else:
        return render_template("dark/admin.html", username="Admin1")


@app.route("/darkholocron/darkholocron/secretmessage")
@login_required
def dark_holocron_secretmessage():
    if login_holo(0) == False:
        return apology("You have to login first!", 404)

    return render_template("dark/troll.html")


# -----------ImperialNet-Part------------------------
@app.route("/imperialnet")
def imperialnetindex():
    return render_template("/imperialnet/imperialnetindex.html")


@app.route("/imperialnet/<username>")
def imperialnet(username):
    # Prepare the username for a case-insensitive match + is vader
    isvader = False
    username_formatted = username.replace("-", " ").title()
    if username_formatted == "Darth Vader":
        isvader = True
    print(isvader)
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
    return render_template("/imperialnet/profile.html", user=user[0], jobs=jobs, skills=skills, isvader=isvader)

    # Ai helped with the sql to speed up the procces, it helped me with the writing of the nice story, also it helped me to design nicer looking pages


@app.route("/imperialnet/comments", methods=['GET', 'POST'])
def imperialcomments():
    if request.method == 'POST':
        comment_text = request.form.get('comment')

        # Check for specific XSS payload pattern
        if detect_xss_payload(comment_text):
            comment_text += " <!-- [Potential XSS detected: IMP-IMP3R1ALXSS] -->"

        # Append the comment
        comments.append({'author': 'Anonymous', 'text': comment_text})

        return redirect(url_for('imperialcomments'))

    return render_template("imperialnet/comments.html", comments=comments)


@app.route("/imperialnet/login")
def imperialnet_login():
    return render_template("/imperialnet/imperiallogin.html")


@app.route("/imperialnet/register")
def imperialnet_register():
    return render_template("/imperialnet/imperialregister.html")

#------------Dark-Archive------------Palpatine-Page-----------


@app.route("/darkarchive/admin")
@login_required
def admin():
    if login_archive(1) == False:
        return apology("You have not gained permission to see this website! You have to login using username from /rebel/score. It will show when you have at least 9 flags. You will also need to guess password (rockyou.txt is a nice file ;))", 66)

    return render_template("darkarchive/admin.html")

@app.route("/darkarchive/adminlogin", methods=['GET', 'POST'])
@login_required
def dark_archive_admin_login():
    if request.method == 'POST':
        user_id = session["user_id"]
        if login_archive(0) == False:
            return apology("You have not gained permission to see this website! Go to /BruteForce in order to succeed", 66)

        # get form
        username = request.form['username']
        password = request.form['password']

        # login into adminarchive
        if username == "1mTheSenatePalp4tine" and password == "Admin123!":
            db.execute("UPDATE users SET archivestage = ? WHERE id = ?", 2, user_id)
            time.sleep(1)
            return redirect("/darkarchive/admin")

    else:
        if login_archive(0) == False:
            return apology("You have not gained permission to see this website! Go to /BruteForce in order to succeed", 66)
        return render_template("darkarchive/adminlogin.html")


@app.route("/darkarchive")
@login_required
def dark_archive():
    if login_archive(0) == False:
        return apology("You have not gained permission to see this website! Go to /BruteForce in order to succeed", 66)

    return render_template("darkarchive/index.html")


@app.route("/darkarchive/palps")
@login_required
def dark_archive_palps():
    if login_archive(0) == False:
        return apology("You have not gained permission to see this website! Go to /BruteForce in order to succeed", 66)

    image_folder = os.path.join('static', 'palpatinememes')
    images = [os.path.join('/static/palpatinememes', f) for f in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, f))]
    return render_template("darkarchive/palps.html", images=images)


if __name__ == "__main__":
    app.run(debug=True)
