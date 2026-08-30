# HackWars CTF - packaged as a self-contained image. The app keeps no shared
# state between processes (Flask signed-cookie sessions, no database writes, no
# filesystem session store), so any number of copies of this image can run side
# by side with zero coordination.

FROM python:3.11-slim

WORKDIR /app

# cs50==9.3.4 / werkzeug==2.0.3 / flask==2.0.3 are old pins that don't build
# on newer Python - 3.11 is the version this was verified against.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# A hosting platform can set the listening port via the PORT env var at deploy
# time; the default here is for local `docker run` convenience.
ENV PORT=8000
EXPOSE 8000

# gunicorn instead of `flask run` - the dev server isn't meant for real
# traffic. Single worker process is required, not just a resource choice:
# app.py keeps the /imperialnet/comments list as an in-process Python list
# with no shared/external store, so multiple worker *processes* would each
# get their own independent copy - a comment posted to one process would
# silently never show up if a later request lands on another, breaking the
# stored-XSS challenge unpredictably. `--threads` gives real concurrency
# within that single process without splitting the in-memory state.
# Threads are set to 24: the scripted brute-force challenges (#7 /BruteForce,
# #9 /darkarchive/adminlogin) push dozens of concurrent requests, and this
# single process serves everyone at once. Only threads scale here, never
# --workers: a second worker process would fork the in-memory comments list and
# break the stored-XSS challenge (see above).
# `exec` replaces the shell (PID 1) so SIGTERM reaches gunicorn directly for
# a clean shutdown, while still expanding $PORT at container start rather
# than build time.
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT} --workers 1 --threads 24 app:app"]

# No curl/wget in python:3.11-slim - reuse the python interpreter already in
# the image instead of installing one just for this check.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python3 -c "import os,urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.environ.get('PORT', '8000') + '/')" || exit 1
