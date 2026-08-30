# HackWars: The Vulnerabilities Strike Back

A Star Wars-themed, deliberately vulnerable Flask web application built as a
self-contained **Capture The Flag (CTF)**. Work through a chain of realistic web
vulnerabilities - XSS, SQL injection, broken access control, information
disclosure, request-header trust, and more - and collect the flags hidden behind
each one. Originally built as a final project for Harvard's **CS50** and later
grown into a full web CTF.

Every flag has the format `CTF{...}`.

> ⚠️ **This app is intentionally insecure.** Run it locally or on an isolated
> host for learning and CTF play only. Never expose it on a network you care
> about.

## Quick start (Docker - recommended)

```bash
cd project
docker compose up --build
```

Then open <http://localhost:8000>. No account or registration - every browser
gets its own anonymous, per-visitor progress automatically.

### Bonus box (privilege escalation + steganography)

One flag lives on a separate SSH "vulnbox". From the repo root:

```bash
docker compose -f docker-compose.bonus.yml up --build   # exposes SSH on :2201
```

## Quick start (local Python - for development)

```bash
cd project
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
flask run            # or: python app.py
```

By default the dev server runs on <http://127.0.0.1:5000>.

Copy [`project/.env.example`](project/.env.example) to `project/.env` and set a
real `SECRET_KEY` before running anywhere others can reach it.

## The challenges

There are 14 flags in total - 13 inside the web app and 1 on the bonus box. They
span social engineering / information disclosure, XSS, several layers of SQL
injection, broken access control (BAC + IDOR), header spoofing, a Caesar cipher,
and a privesc-to-steganography chain on the bonus box.

- **[`project/CHALLENGES.md`](project/CHALLENGES.md)** - the flag catalog with
  category and difficulty (0-5) for each.
- **[`project/SOLUTIONS.md`](project/SOLUTIONS.md)** - full solve writeups
  (**spoilers**).

## Notes

- Parts of the in-story flavor text and page styling were drafted with AI help.
- The app ships some deliberate anti-automation decoys (a token "tarpit" and
  wrong-format decoy strings like `CTF[...]`); only `CTF{...}` is ever a real
  flag.
