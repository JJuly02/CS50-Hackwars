import re
from flask import render_template

# What the comment filter strips. Each pattern is applied in a single pass
# over the incoming text and the result is never re-scanned - which is the
# whole point. That is the mistake real "we sanitise input" code makes, and it
# means a token split across itself reassembles after the removal:
#
#   <scr<script>ipt>alert(1)</scr</script>ipt>  ->  <script>alert(1)</script>
#   <img src=x oonerror=nerror=alert(1)>        ->  <img src=x onerror=alert(1)>
#
# Do not "fix" this into a loop or a real sanitiser - the bypass IS challenge
# #5. Before 2026-08-09 there was no filter at all and a bare <script> tag
# scored on the first try, which is not an exercise for anyone, least of all
# for a player working with an AI assistant.
_SCRIPT_TAG = re.compile(r"<\s*/?\s*script[^>]*>", re.IGNORECASE)
# No \b anchor and a lazy \w+? on purpose. Anchored and greedy, this pattern
# swallows a split attribute whole ("oneonerror=rror=" matches end to end) and
# the event-handler vector becomes unbeatable, leaving tag nesting as the only
# way through. Written like this, splitting the token works on handlers too, so
# the same lesson applies to both vectors.
_EVENT_ATTR = re.compile(r"on\w+?\s*=", re.IGNORECASE)
_JS_URI = re.compile(r"javascript:", re.IGNORECASE)

# Fires only on markup that would actually execute once stored. Deliberately
# narrower than the filter above: a bare <img> or <svg> is not XSS, and
# rewarding it would hand out the flag for typing a harmless tag. This is
# evaluated on the text AFTER filtering, so only a real bypass scores.
_XSS_PATTERN = re.compile(r"<\s*script|\bon\w+\s*=|javascript:", re.IGNORECASE)


def sanitize_comment(text):
    """Strip the obvious XSS vectors - once each, no re-scan. See above."""
    cleaned = _SCRIPT_TAG.sub("", text)
    cleaned = _EVENT_ATTR.sub("", cleaned)
    cleaned = _JS_URI.sub("", cleaned)
    return cleaned


def detect_xss_payload(text):
    return bool(_XSS_PATTERN.search(text))


def apology(message, code=400):
    # `code` doubles as the in-game "Error Code" flavor text (e.g. 66),
    # which is often not a real HTTP status.
    # A 2-digit status line is invalid HTTP/1.1 and gets dropped by strict
    # clients/proxies (confirmed with curl - "Unsupported HTTP/1 subversion
    # in response") - almost certain to break behind a production reverse proxy.
    # Show the flavor number on the page, but always send a valid status.
    http_status = code if 100 <= code <= 599 else 400
    return render_template("rebel/apology.html", top=code, bottom=message), http_status
