import ipaddress
import os
import sys
from functools import wraps
from cs50 import SQL
from flask import Flask, render_template, request, redirect, session, Response
import time
from werkzeug.security import check_password_hash

from helper import apology, detect_xss_payload, sanitize_comment
from tarpit import (
    render_tarpit, config_bak, api_keys, dump_sql, env_leak, git_config, debug_status,
)

app = Flask(__name__)

# SECRET_KEY must come from the environment in any deployed instance -
# the dev fallback below is only safe for local `flask run`. Progress state
# lives entirely in the signed session cookie with no server-side check, so
# a leaked/default key lets anyone forge a cookie that skips every stage.
if "SECRET_KEY" not in os.environ:
    print(
        "WARNING: SECRET_KEY is not set - using an insecure default. "
        "Set the SECRET_KEY environment variable before deploying.",
        file=sys.stderr,
    )
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-insecure-key-change-me")

# No accounts/login: CTFd owns auth, scoring and flag submission. This app
# only needs to remember how far *this browser* has gotten in the story, so
# every visitor gets Flask's default signed-cookie session (no filesystem
# session store - nothing here is secret, and it avoids writing a session
# file to disk for every single request/asset, plus works unmodified across
# multiple app instances since there's no shared server-side store to pin).
@app.before_request
def init_progress():
    session.setdefault("holocronstage", 0)
    session.setdefault("archivestage", 0)
    session.setdefault("sqli_admin1", False)
    session.setdefault("bac_admin_panel", False)


# Discourage AI crawlers/agents from indexing or auto-solving the CTF
@app.after_request
def add_ai_headers(response):
    response.headers["X-Robots-Tag"] = "noai, noimageai"
    return response


@app.route("/robots.txt")
def robots_txt():
    return app.send_static_file("robots.txt")


# Anti-AI tarpit / token sink (see tarpit.py). NOT a real challenge: a finite,
# deterministically-generated, cached maze that taxes automated "read the whole
# site and solve it" tools which ignore the aria-hidden notice and robots.txt.
# Discoverable only via robots.txt; nothing in the human UI links here. Every
# decoy "flag" inside uses CTF[...] (square brackets, not braces), so it looks
# flag-like at a glance but can never match a real CTF{...} flag in CTFd.
@app.route("/imperial-archive")
@app.route("/imperial-archive/<int:node>")
def imperial_archive(node=0):
    return render_tarpit(node)


# Smaller sinkholes planted at the classic recon paths an automated scanner
# probes but a human following the story never touches (leaked config, exposed
# .git, a SQL dump, an enumerable API, a debug endpoint). All decoys are
# CTF[...], all bounded/cached (see tarpit.py). A curated set on purpose - NOT
# a catch-all on every 404: if every unknown path returned a juicy secret, the
# uniformity would itself scream "honeypot" and get the whole site skipped.
def _sinkhole(pair):
    body, content_type = pair
    return Response(body, mimetype=content_type)


@app.route("/config.bak")
def sink_config():
    return _sinkhole(config_bak())


@app.route("/.env")
def sink_env():
    return _sinkhole(env_leak())


@app.route("/.git/config")
def sink_git():
    return _sinkhole(git_config())


@app.route("/backup/dump.sql")
def sink_dump():
    return _sinkhole(dump_sql())


@app.route("/api/keys")
def sink_api():
    page = request.args.get("page", default=0, type=int)
    return _sinkhole(api_keys(page))


@app.route("/debug")
def sink_debug():
    return _sinkhole(debug_status())

# Konfiguracja bazy danych
dbimperial = SQL("sqlite:///databases/imperialnet.db")  # imperial page
dbholocron1 = SQL("sqlite:///databases/hint.db")  # darkholocron
palpdb = SQL("sqlite:///databases/palps.db")  # palpatine page

# In-memory comments
comments = [
    {'author': 'Colonel Yularen', 'text': 'This page is an excellent resource for the Empire.'},
    {'author': 'Clone Trooper Fives', 'text': 'Affirmative, this page greatly aids our mission.'},
    {'author': 'Clone Trooper Echo', 'text': 'Impressive layout! Very informative.'}
]

# The list above lives in the process and is shared by every visitor of this
# instance, so it needs a ceiling for two reasons: it would otherwise grow for
# as long as the container runs, and a payload that hijacks the page for
# everyone (`<script>window.location=...</script>`) has to be able to scroll
# off eventually instead of bricking the XSS challenge until a restart.
SEED_COMMENT_COUNT = len(comments)
MAX_PLAYER_COMMENTS = 20


def login_holo(n):
    if session["holocronstage"] < n:
        return False


def login_archive(n):
    if session["archivestage"] < max(n, 1):
        return False


def holo_stage_required(n):
    """Gate a dark-holocron route behind holocronstage >= n."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if login_holo(n) == False:
                return apology("You have to login first!", 404)
            return f(*args, **kwargs)
        return wrapped
    return decorator


def archive_stage_required(n, message="You have not gained permission to see this website! Go to /BruteForce in order to succeed"):
    """Gate a dark-archive route behind archivestage >= n."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if login_archive(n) == False:
                return apology(message, 66)
            return f(*args, **kwargs)
        return wrapped
    return decorator


@app.route("/")
def index():
    return render_template("/rebel/index.html")


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
    if request.method == 'POST':
        # "" rather than None - check_password_hash(hash, None) raises, which
        # turned a mistyped field name in a player's brute-force script into an
        # opaque 500 instead of a plain "wrong keywords" answer.
        keyword1 = request.form.get("keyword1", "")
        keyword2 = request.form.get("keyword2", "")

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
            if session["archivestage"] < 1:
                session["archivestage"] = 1
            time.sleep(1)
            return redirect("/BruteForce/animation")
        else:
            return redirect("/BruteForce/animation")
    else:
        return render_template("rebel/bruteforce.html")

@app.route("/BruteForce/animation", methods=["GET"])
def video():
    success = session["archivestage"] >= 1
    return render_template("rebel/brutevideo.html", message="Attempting Brute Force Attack...", success=success)

#------------Dark-Holocron-------------Vader-Page-----------
@app.route("/darkholocron", methods=['GET', 'POST'])
def dark_holocron():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Insecure SQL query that is vulnerable to SQL injection
        try:
            query = dbholocron1.execute(f"SELECT id, username FROM holocron WHERE username = '{username}' AND pass = '{password}'")
        except Exception:
            # A malformed statement surfaces as a database error and nothing
            # more. This used to echo the interpolated query back to the player
            # ("Query executed: SELECT id FROM holocron WHERE username = '...'"),
            # which handed over the vulnerability class, the injection point and
            # the payload shape in one screen. The bare error still tells anyone
            # who tries a stray quote that their input reaches the engine, which
            # is how an injectable form gets noticed in the wild - without
            # printing the answer.
            return render_template("dark/mlogin.html", message="Imperial database error. Report to Imperial IT with the time of this request.")

        if not query:
            return render_template("dark/mlogin.html", message="Access denied.")

        user = query[0]["username"]

        if user != "Admin1":
            if session["holocronstage"] == 0:
                session["holocronstage"] = 1
            return redirect(f"/darkholocron/{user}")

        elif user == "Admin1":
            session["holocronstage"] = 2
            # Tracked separately from holocronstage on purpose: the broken
            # access control challenge also pushes the stage to 2, so keying
            # the Admin1 flag off the stage alone would hand out Level 3 to
            # anyone who took the BAC flag with a generic payload.
            session["sqli_admin1"] = True
            return redirect(f"/darkholocron/Admin1")
    else:
        return render_template("dark/mlogin.html")

# Broken access control
@app.route("/darkholocron/<username>")
def dark_holocron_holocron(username):
    is_skywalker = False
    is_sith_lord = True

    # Check whether the requested profile is Darth Vader or Emperor Palpatine
    is_admin1 = False
    if username == "DarthVader":
        username_display = "Darth Vader"
        is_skywalker = True
    elif username == "EmperorPalpatine":
        username_display = "Emperor Palpatine"
    else:
        username_display = username.replace("-", " ").title()
        is_sith_lord = False
        # This route is deliberately open (any name renders a profile page),
        # so the Admin1 flag can't hang on the URL alone - /darkholocron/sith
        # names the account out loud, which made the whole Level 3 challenge
        # guessable without ever touching the login form. sqli_admin1 is set
        # only by an injection that resolves specifically to that account.
        is_admin1 = (username == "Admin1" and session.get("sqli_admin1", False))

    return render_template("dark/holocron.html", username=username_display, is_sith_lord=is_sith_lord, is_skywalker=is_skywalker, is_admin1=is_admin1)


@app.route("/darkholocron/sith")
@holo_stage_required(0)
def dark_holocron_sith():
    # The page itself stays open to everyone - it's the discovery path to the
    # Level 0 trap. The intel on it (the SithCode keyword, the Admin1 account)
    # is what needs earning: handed out at stage 0 it shortcuts a Level 2 and
    # a Level 3 challenge before the player has done anything at all.
    return render_template("dark/sith.html", show_intel=session["holocronstage"] >= 1)


@app.route("/darkholocron/skywalker")
@holo_stage_required(1)
def dark_holocron_skywalker():
    return render_template("dark/skywalker.html")

# Personnel records the admin panel's user-lookup feature serves. Kept as a
# curated dict rather than reading the holocron auth table, so a record lookup
# can never dump password material. `id` 5 is the account the panel logs you in
# as; the Death Star access code (#8) lives on id 6, the Emperor's record, so it
# is no longer printed just for loading the page - see the route below.
ADMIN_RECORDS = {
    1: {"name": "Darth Vader", "title": "Supreme Commander of the Imperial Fleet", "clearance": "Sith Lord", "note": "Personal terminal, restricted."},
    2: {"name": "Colonel Yularen", "title": "ISB Deputy Director", "clearance": "Imperial Security", "note": "Loyalty verified."},
    3: {"name": "Grand Moff Tarkin", "title": "Governor of the Outer Rim", "clearance": "Grand Moff", "note": "Overseeing Project Stardust."},
    4: {"name": "Admiral Thrawn", "title": "Grand Admiral", "clearance": "Fleet Command", "note": "Whereabouts classified."},
    5: {"name": "Admin1", "title": "Holocron System Account", "clearance": "Administrator", "note": "Automated maintenance account. This is you."},
    6: {"name": "Emperor Palpatine", "title": "Galactic Emperor", "clearance": "OMEGA - EYES ONLY", "note": "Death Star access code: CTF{4DM1NCON7R0L}"},
}
# The account the panel considers "you". Any other id is someone else's record.
CURRENT_ADMIN_ID = 5


@app.route("/darkholocron/admin", methods=['GET', 'POST'])
def dark_holocron_admin():
    holostage = session["holocronstage"]

    if holostage < 1:
        return apology("You have to login first!", 404)

    # The BAC flag is earned by reaching this panel without ever authenticating
    # as an admin - equally true whether the player arrived on stage 1 (generic
    # payload) or jumped straight to stage 2 with the targeted Admin1 injection.
    # Keying it off `holostage == 1` alone made the flag permanently unreachable
    # for anyone who solved the harder Level 3 injection first: that path sets
    # the stage to 2 up front, so the panel rendered without the flag on every
    # visit and nothing ever put the session back. Tracked on its own session
    # key, like sqli_admin1, so it stays a one-shot award either way.
    message = None
    if not session.get("bac_admin_panel", False):
        session["bac_admin_panel"] = True
        message = "Broken access control - CTF{BROK3NKONTROL}"

    if holostage == 1:
        session["holocronstage"] = 2

    # #8 used to sit in the page body, so #6 and #8 both landed on one page load
    # - 500 pts for a single click, and the harder-first player could still miss
    # #6 (see above). It is now behind an IDOR: the record viewer trusts the
    # client-supplied `uid` and does no ownership check, so stepping the id off
    # your own record (5) onto the Emperor's (6) reveals the access code. Loading
    # the panel alone shows only your own record and no flag.
    requested_uid = request.args.get("uid", default=CURRENT_ADMIN_ID, type=int)
    record = ADMIN_RECORDS.get(requested_uid)
    is_own_record = requested_uid == CURRENT_ADMIN_ID

    return render_template(
        "dark/admin.html",
        message=message,
        username="Admin1",
        record=record,
        record_id=requested_uid,
        is_own_record=is_own_record,
        current_admin_id=CURRENT_ADMIN_ID,
    )


@app.route("/darkholocron/darkholocron/secretmessage")
@holo_stage_required(0)
def dark_holocron_secretmessage():
    return render_template("dark/troll.html")


# -----------ImperialNet-Part------------------------
@app.route("/imperialnet")
def imperialnetindex():
    return render_template("/imperialnet/imperialnetindex.html")


@app.route("/imperialnet/<username>")
def imperialnet(username):
    # Prepare the username for a case-insensitive match + is vader
    isvader = False
    is_inquisitor = False
    username_formatted = username.replace("-", " ").title()
    if username_formatted == "Darth Vader":
        isvader = True
    elif username_formatted == "Grand Inquisitor":
        is_inquisitor = True
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
    return render_template("/imperialnet/profile.html", user=user[0], jobs=jobs, skills=skills, isvader=isvader, is_inquisitor=is_inquisitor)

    # Ai helped with the sql to speed up the procces, it helped me with the writing of the nice story, also it helped me to design nicer looking pages


@app.route("/imperialnet/comments", methods=['GET', 'POST'])
def imperialcomments():
    if request.method == 'POST':
        # Default to "" rather than None: a POST without the field (a player's
        # script with a typo in the field name) used to blow up in the regex
        # with a 500 instead of just showing an empty comment.
        comment_text = request.form.get('comment', '')
        # Stored XSS: what survives the filter is rendered with |safe below.
        # Both the storage and the flag check run on the *sanitised* text, so a
        # payload the filter neutralises scores nothing - only a real bypass
        # does. Checking the raw input instead would hand out the flag for a
        # blocked payload, which is what happens if these two lines drift apart.
        stored_text = sanitize_comment(comment_text)
        comments.append({
            'author': 'Anonymous',
            'text': stored_text,
            'flagged': detect_xss_payload(stored_text),
        })
        # Drop the oldest player comments past the cap, never the seeds. With
        # fewer comments than the cap this slice is empty, so it's a no-op.
        del comments[SEED_COMMENT_COUNT:-MAX_PLAYER_COMMENTS]

    return render_template("imperialnet/comments.html", comments=comments)


@app.route("/imperialnet/login")
def imperialnet_login():
    # "VLAN check" - trusts whatever the client claims via X-Forwarded-For
    # instead of validating a real proxy chain, so it's spoofable with a
    # single request header.
    forwarded_for = request.headers.get("X-Forwarded-For", "")
    claimed_ip = forwarded_for.split(",")[0].strip()
    # Parse the address instead of matching the "10.66.6." prefix as a string -
    # that let 10.66.6.66666 through, which is a sloppier check than the flaw
    # this challenge is meant to teach.
    try:
        on_imperial_network = (
            ipaddress.ip_address(claimed_ip) in ipaddress.ip_network("10.66.6.0/24")
        )
    except ValueError:
        on_imperial_network = False
    return render_template(
        "/imperialnet/imperiallogin.html",
        on_imperial_network=on_imperial_network,
    )


@app.route("/imperialnet/register")
def imperialnet_register():
    return render_template("/imperialnet/imperialregister.html")

#------------Dark-Archive------------Palpatine-Page-----------


@app.route("/darkarchive/admin")
@archive_stage_required(2, "You have not gained permission to see this website! Read the intel on /darkarchive first, then run the recovered credential dump against /darkarchive/adminlogin.")
def admin():
    return render_template("darkarchive/admin.html")

@app.route("/darkarchive/adminlogin", methods=['GET', 'POST'])
@archive_stage_required(0)
def dark_archive_admin_login():
    if request.method == 'POST':
        # get form
        username = request.form['username']
        password = request.form['password']

        # login into adminarchive
        # Password is DarkTr00per_66 - deliberately not a top-of-mind "weak
        # admin password" (Admin123!, Password1, admin...), because an assistant
        # guesses those in its first few tries and the challenge evaporates. It
        # sits in static/imperial_creds_leak.txt (line ~106 of 151) with those
        # obvious guesses planted as non-matching decoys, so the intended solve
        # is actually running the recovered dump against this form.
        if username == "1mTheSenatePalp4tine" and password == "DarkTr00per_66":
            session["archivestage"] = 2
            time.sleep(1)  # only on success - a one-off flourish, not a per-try
                           # delay. A failure-side sleep would pin a thread on
                           # single-worker gunicorn and let a player's own
                           # brute-force script DoS their team's instance.
            return redirect("/darkarchive/admin")

        # No lockout and no failure delay on purpose: the dump is meant to be
        # run against this form. The cost that makes it a real exercise is the
        # list length, not artificial throttling.
        return apology("Invalid username and/or password", 400)

    else:
        return render_template("darkarchive/adminlogin.html")


@app.route("/darkarchive")
@archive_stage_required(0)
def dark_archive():
    return render_template("darkarchive/index.html")


@app.route("/darkarchive/palps")
@archive_stage_required(0)
def dark_archive_palps():
    image_folder = os.path.join('static', 'palpatinememes')
    images = [os.path.join('/static/palpatinememes', f) for f in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, f))]
    return render_template("darkarchive/palps.html", images=images)


if __name__ == "__main__":
    # A hosting platform may set PORT; debug must stay off unless FLASK_DEBUG=1
    # is explicitly set for local development - the Werkzeug debugger allows
    # arbitrary code execution and must never run on a public deployment.
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=os.environ.get("FLASK_DEBUG") == "1",
    )
