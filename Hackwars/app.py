import os
import re
from cs50 import SQL
from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import datetime

from helper import login_required, login_requiredarch, apology

app = Flask(__name__)

# session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Konfiguracja bazy danych
dbimperial = SQL("sqlite:///imperialnet.db")
db = SQL("sqlite:///users.db")
dbholocron1 = SQL("sqlite:///hint.db")
dbvader = SQL("sqlite:///vader.db")

@app.route("/")
@login_required
def index():
    return render_template("/rebel/index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    #TODO Logika logowania
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
    #TODO Logika rejestarcji
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

        # TODO require the same password again to check if it's correct
        if not repassword:
            return apology("Must provide password confirmation", 46)

        if repassword != password:
            return apology("Password confirmation is not the same as password", 47)

        # Sumbit
        try:
            rows = db.execute(
                "INSERT INTO users (username, hashpass) VALUES (?, ?)", request.form.get("username"), generate_password_hash(password)
            )
        except:
            return apology("User arleady exist!", 48)

        return render_template("/rebel/register.html")

        # TODO Render similar to login page but for the register with to places for password
    else:
        return render_template("/rebel/register.html")

@app.route("/logout")
def logout():
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/score")
@login_required
def score():
    user_id = session["user_id"]
    user_data = db.execute("SELECT username, holocronstage, holoscore, archscore, imperialscore, score FROM users WHERE id = ?", (user_id,))

    if user_data:
        # Extracting each score into a separate variable
        holocronstage = user_data[0]['holocronstage']
        holoscore = user_data[0]['holoscore']
        archscore = user_data[0]['archscore']
        imperialscore = user_data[0]['imperialscore']
        total_score = user_data[0]['score']
        username = user_data[0]["username"]

        # Passing each score as a separate variable to the template
        return render_template("rebel/score.html", holocronstage=holocronstage, holoscore=holoscore, archscore=archscore, imperialscore=imperialscore, total_score=total_score, username=username)
    else:
        return apology("Score data not found.", 404)


#------------Dark-Holocron-------------Vader-Page-----------
darkdb = SQL("sqlite:///hint.db")

@app.route("/darkholocron", methods=['GET', 'POST'])
def dark_holocron():
    message = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Insecure SQL query that is vulnerable to SQL injection
        query = dbholocron1.execute(f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'")
        message = 'Query executed: ' + query

        loginquery = query = dbholocron1.execute(f"SELECT username, password FROM users WHERE username = '{username}' AND password = '{password}'")

        if loginquery[0] == username and loginquery[1] == password:
            return redirect("/darkholocron/holocron")
        else:
            return render_template("dark/index.html", message=message)

    else:
        return render_template("dark/index.html", message=message)


@app.route("/darkholocron/holocron")
def dark_holocron_holocron():
    return render_template("dark/holocron.html")

@app.route("/darkholocron/sith")
def dark_holocron_sith():
    return render_template("dark/sith.html")

#here it can be time based searching wheather its possible to hack
@app.route("/darkholocron/admin", methods=['GET', 'POST'])
def dark_holocron_admin():
    return render_template("dark/admin.html")

@app.route("/darkholocron/4a3aa5b4acbfda994476564ff8a36f5e", methods=['GET', 'POST'])
def dark_holocron_login3():
    return render_template("dark/loginvader.html")

# -----------ImperialNet-Part------------------------
@app.route("/imperialnet")
def imperialnetindex():
    return render_template("/imperialnet/imperialnetindex.html")

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
    return render_template("/imperialnet/profile.html", user=user[0], jobs=jobs, skills=skills)

    # Ai helped with the sql to speed up the procces, it helped me with the writing of the nice story, also it helped me to design nicer looking pages

@app.route("/imperialnet/login")
def imperialnet_login():
    return render_template("/imperialnet/imperiallogin.html")

@app.route("/imperialnet/register")
def imperialnet_register():
    return render_template("/imperialnet/imperialregister.html")

#Insufficent acces control TODO


#------------Dark-Archive------------Palpatine-Page-----------
commandb = SQL("sqlite:///admins.db")
@app.route("/darkarchive")
def dark_archive():
    return render_template("darkarchive/index.html")

@app.route("/darkarchive/login")
def dark_archive_login():
    return render_template("darkarchive/login.html")

@app.route("/darkarchive/palps")
@login_requiredarch
def dark_archive_palps():
    return render_template("darkarchive/login.html")

if __name__ == "__main__":
    app.run(debug=True)

