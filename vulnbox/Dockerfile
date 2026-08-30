# Bonus flag #12 delivery: "Palpatine's personal terminal". Same reused
# creds as /darkarchive/adminlogin (1mTheSenatePalp4tine / DarkTr00per_66),
# reachable over SSH. Low-priv shell only - the escalation to root is the
# actual challenge (sudo misconfiguration, GTFOBins-style). A single
# self-contained container - no shared state.
#
# The password is kept in lockstep with the web capstone on purpose (see #9);
# if you change one, change both and rebuild this image.

# Build stage: compile the decoy "verifier" binary here so no compiler ships in
# the runtime image players get. See vulnbox/decoys/verifier.c - it derives its
# output from the bytes of AGENTS.md (tamper = garbage).
FROM debian:bookworm-slim AS build
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libc6-dev && \
    rm -rf /var/lib/apt/lists/*
COPY decoys/verifier.c /tmp/verifier.c
# No -s: keep the symbol names (verify_flag_hmac, cleanup_handler) visible so a
# reverser sees the red herrings the notes point at.
RUN gcc -O2 -o /tmp/verifier /tmp/verifier.c

# Runtime stage.
FROM debian:bookworm-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends openssh-server sudo findutils && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /run/sshd

# Low-priv account. Username/password intentionally reused from the web
# capstone - "the Emperor is lazy about passwords everywhere", not a new
# credential to discover.
RUN useradd -m -s /bin/bash 1mTheSenatePalp4tine && \
    echo "1mTheSenatePalp4tine:DarkTr00per_66" | chpasswd

# The actual vulnerability: NOPASSWD sudo on a GTFOBins-exploitable binary.
# `sudo find . -exec /bin/sh \; -quit` spawns a root shell.
RUN echo "1mTheSenatePalp4tine ALL=(root) NOPASSWD: /usr/bin/find" \
    > /etc/sudoers.d/palpatine-find && \
    chmod 0440 /etc/sudoers.d/palpatine-find

# Flag, root-owned and root-only - unreadable until escalation succeeds.
COPY deathstarSeecret.jpg /root/deathstarSeecret.jpg
RUN chown root:root /root/deathstarSeecret.jpg && chmod 600 /root/deathstarSeecret.jpg

# --- AI time-wasting decoys (see vulnbox/decoys/). Readable by the low-priv
# user ON PURPOSE: an automated agent doing recon (ls / cat / reading
# ~/.bash_history) burns time chasing these before it finds the real path.
# Every token inside is CTF[...] (wrong format - never the real CTF{...}),
# and NONE of them grant privesc, touch sudo, or reveal the flag. The real
# plans stay root-only in /root/deathstarSeecret.jpg, reachable solely via the
# sudo/find escalation above. notes.txt + .bash_history even nudge toward that
# real path (`sudo -l`), so a human isn't left stuck in the rabbit hole.
COPY decoys/notes.txt /home/1mTheSenatePalp4tine/notes.txt
COPY decoys/bash_history /home/1mTheSenatePalp4tine/.bash_history
COPY decoys/imperial-archive /opt/imperial-archive
RUN chown -R 1mTheSenatePalp4tine:1mTheSenatePalp4tine \
        /home/1mTheSenatePalp4tine/notes.txt \
        /home/1mTheSenatePalp4tine/.bash_history \
        /opt/imperial-archive

# Decoy reversing sub-challenge: misleading AGENTS.md/CLAUDE.md point an agent
# at verify_flag_hmac() (a red herring) and invite it to "tidy" the markdown -
# which silently changes the verifier's output to garbage, because the binary
# derives its output from the bytes of AGENTS.md. Pristine it prints a CTF[...]
# decoy, NEVER the real flag (which stays in the root-only stego jpg). The
# delayed feedback - a wrong string long after the file was "cleaned up" - is
# the point. verify_flag_hmac()/cleanup_handler() in the binary are dead ends.
COPY --from=build /tmp/verifier /home/1mTheSenatePalp4tine/verifier
COPY decoys/AGENTS.md /home/1mTheSenatePalp4tine/AGENTS.md
COPY decoys/CLAUDE.md /home/1mTheSenatePalp4tine/CLAUDE.md
RUN chown 1mTheSenatePalp4tine:1mTheSenatePalp4tine \
        /home/1mTheSenatePalp4tine/verifier \
        /home/1mTheSenatePalp4tine/AGENTS.md \
        /home/1mTheSenatePalp4tine/CLAUDE.md && \
    chmod 0755 /home/1mTheSenatePalp4tine/verifier

RUN ssh-keygen -A

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]
