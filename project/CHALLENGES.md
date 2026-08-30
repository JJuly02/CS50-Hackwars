# Challenge catalog (CTFd category/level model)

This maps every flag in HackWars to a **category** and **level (0-5)**
difficulty model.

HackWars stays a single continuous Flask app (story-driven, sequential
unlocks) rather than one-challenge-per-container, so this table is the
reference mapping — not a folder-per-challenge layout. `ctfd/challenges.yml`
gives the same data in a ctfcli-importable shape, in case any of these are
ever lifted into a real CTFd instance as standalone challenges.

**No accounts/login/scoreboard in this app** — the app just tracks the
sequential story unlocks (`holocronstage`/`archivestage`) so pages reveal in
order, as an anonymous per-browser session, not a rebel account.

Sorted below by level and points, ascending. `ID` is the numbering used in
`SOLUTIONS.md` — it's a stable identifier, not a solve order, so it doesn't
run 1..14 in this sorted view. (`ctfd/challenges.yml` has no numbers of its
own; its entry order follows this file's old, pre-2026-08-06 table, so go by
the flag string when matching entries between the two.)

Descriptions are deliberately spoiler-free (no vulnerability class named).
Hints are a level more concrete, for players stuck after the description
alone. **This file is not linked from the game** — the homepage mentions it
by name, but the link there points at CTFd's own docs. Keep it that way: the
tables below list every flag in cleartext.

## Level 0 — 50 pts each — Web Security

| ID | Challenge | Where | Flag |
|----|-----------|-------|------|
| 1 | View-source easter egg | `/` (Rebel index) | `CTF{R3B3L10N}` |
| 2 | HTML comment leak | `/imperialnet` | `CTF{1MP3R1AL}` |
| 3 | The trap redirect | `/darkholocron/darkholocron/secretmessage` | `CTF{17S_4_TR4P}` |
| 13 | Patience easter egg | `/` (Rebel index) | `CTF{P4T13NC3_YOUNG_P4DAW4N}` |

- **#1 —** *"Hidden in plain sight, some secrets are. Look with more than your
  eyes, you must."*
  **Hint:** Check the raw HTML of the homepage — not everything is meant to
  be seen only through the browser's rendering.
- **#2 —** *"In a hurry, this page was built. Careless, developers sometimes
  are, hmm."*
  **Hint:** View the page source of `/imperialnet` and look near the end of
  the markup.
- **#3 —** *"Not everything unseen, forbidden is. Sometimes, exactly a trap,
  a trap is."*
  **Hint:** The Dark Holocron login page's source hints at a page linked
  before it should be — follow that thread.
- **#13 —** *"Patience, you must have, young Padawan. Reward, the end of the
  story brings."*
  **Hint:** Read the opening crawl on the homepage all the way to its final
  lines.

## Level 1 — 150 pts each — Web Security

| ID | Challenge | Where | Flag |
|----|-----------|-------|------|
| 11 | ImperialNet profile enumeration | `/imperialnet/<name>` | `CTF{R3DS4B3R}` |
| 4 | Skywalker Chronicles (BAC chain) | `/darkholocron/skywalker` | `CTF{PH4NT0MMEN4C3}` |
| 14 | ImperialNet login bypass (easter egg) | `/imperialnet/login` | `CTF{TRUST_NO_H34D3R}` |

- **#11 —** *"Only a few names, the index shows you. More servants of the
  Empire, there are, I sense."*
  **Hint:** The profile page accepts more names than the ones linked on
  `/imperialnet`. `/darkarchive` and `/robots.txt` both nod toward one you
  haven't seen.
- **#4 —** *"A page for a Skywalker alone, this is. Yet loosely guarded, the
  way there is."*
  **Hint:** Get past the Dark Holocron's login first (any attempt that
  returns a result works), then visit this page directly.
- **#14 —** *"Believe what it's told without question, this door does. What
  you claim to be matters more than what you are."*
  **Hint:** View the page source — a leftover developer note explains
  exactly what this login page checks, and how.

## Level 2 — 250 pts each — Web Security

| ID | Challenge | Where | Flag |
|----|-----------|-------|------|
| 5 | Stored XSS in comments (filter bypass) | `/imperialnet/comments` | `CTF{IMP3R1ALXSS}` |
| 6 | Broken access control | `/darkholocron/admin` | `CTF{BROK3NKONTROL}` |
| 7 | Weak credentials brute force | solved at `/BruteForce`, flag shown on `/darkarchive` | `CTF{4CC3SS_6R4N73D}` |
| 8 | Death Star access code (IDOR) | `/darkholocron/admin?uid=6` | `CTF{4DM1NCON7R0L}` |

- **#5 —** *"Every word you leave, this page repeats to others — but now a
  guard reads it first."*
  **Hint:** A filter strips the obvious script tags and event handlers, but
  only once and without looking again. Split the dangerous part across itself
  so removing the inner copy leaves a working payload behind.
- **#6 —** *"Careful with some doors, the Empire is. Others, it forgets to
  check at all."*
  **Hint:** After any successful-looking login at `/darkholocron`, a link to
  an admin panel appears — visit it.
- **#7 —** *"Lazy with secrets, the Empire is. Somewhere, a list of its
  favorite words, waits."*
  **Hint:** `/ImperialWebscraper` links to a larger, unfiltered word dump —
  try pairs of words from it at `/BruteForce`.
- **#8 —** *"Two secrets, one room. How you got in, and what you find once
  inside, the same thing they are not."*
  **Hint:** The admin panel shows a personnel record addressed by a numeric
  `uid` in the URL, defaulting to your own. Ask it for a record that isn't
  yours — the Emperor's.
  **Redesigned 2026-08-09 (was: same page as #6).** #8 used to print in the
  panel body, so #6+#8 paid 500 pts for one click, and a targeted-injection
  player could miss #6 entirely (see #10). #8 is now an **IDOR** behind
  `?uid=`: loading the panel earns only #6, and reading the Emperor's record
  (`uid=6`) earns #8. Two distinct actions, two vulnerability classes. #6 is
  awarded on first arrival regardless of which injection opened the panel,
  tracked on its own session key so it stays one-shot.

## Level 3 — 350 pts each — Web Security

| ID | Challenge | Where | Flag |
|----|-----------|-------|------|
| 10 | Dark Holocron SQL injection (targeted) | `/darkholocron` | `CTF{4DM1NP4N3L}` |
| 9 | Death Star capstone | `/darkarchive/admin` | `CTF{M4Y_7H3_F0RC3_B3_W17HY0}` |

- **#10 —** *"Trust your words too much, this login does. Precise, you must
  be, to reach the one you truly seek."*
  **Hint:** The login form builds its query directly from your input. A
  generic "always true" login gets you in as someone — but as *whom*? The
  login sends you onward addressed by the account it matched, so vary the
  injection to land on different rows and read the redirect until the hidden
  privileged account surfaces, then target it by name.
  The flag only appears if the injection actually resolved to that account;
  visiting the URL, or arriving there off a generic payload, shows nothing.
  **Redesigned 2026-08-09:** the sith page used to name the `Admin1` account
  outright, reducing this to typing a handed-over string. The name is now
  discoverable only by enumerating through the login (the redirect leaks the
  matched username); the hint text points at the technique, not the name.
  **Note for organizers (2026-08-09):** the in-game hints were deliberately
  cut back, and the reason is not that they were too generous in the
  abstract — it is that the difficulty here is calibrated against players who
  have an AI assistant open. A model handed the old page solved this in one
  step: the source named the vulnerability class and the echo printed the
  interpolated statement, so there was nothing left to work out. The bar is
  set for that player, not for someone working without one. Do not restore
  these as
  "lost hints". `/darkholocron` used to echo the interpolated query back to the
  player on any failed login (`Query executed: SELECT id FROM holocron WHERE
  username = '...'`), and the page source carried a devnote spelling out
  f-string concatenation, missing escaping and the single-quote break. Both
  are gone; the source now only says the login was rushed and never reviewed.
  What remains is the realistic discovery signal — a stray quote returns
  *"Imperial database error"* while ordinary wrong credentials return
  *"Access denied"*, so probing still tells the player their input reaches
  the engine. Watch this at the event: `holocronstage >= 1` gates #4, #6, #8,
  #10 and the `SithCode` keyword (hence #7, #9 and bonus #12), so a room that
  cannot find the injection loses 7 of the 11 required flags, not one. If it
  stalls, hint verbally rather than reverting.
- **#9 —** *"Many steps, the final door requires. Alone, none of them open
  it — together, they do."*
  **Hint:** Chain what you learned from the brute-force step and the admin
  login step — both are required, in order, to reach this page. The username is
  on `/darkarchive`; the password is in the leaked dump linked there, so run
  the list against `/darkarchive/adminlogin`.
  **Redesigned 2026-08-09:** the password was `Admin123!` — a guess an AI
  assistant makes in its first few tries, so the dictionary attack was
  decorative. It is now `DarkTr00per_66`, planted in
  `static/imperial_creds_leak.txt` (~line 106 of 151) with the obvious guesses
  seeded as non-matching decoys. No lockout/no per-attempt delay by design; the
  list length is the cost. Reused as the vulnbox SSH password (#12) — change
  one, change both and rebuild the image.

## Level 4 — bonus, 450 pts — Pwn / Forensics

| ID | Challenge | Where | Flag |
|----|-----------|-------|------|
| 12 | Bonus: privesc + steganography | SSH via `vulnbox/` (separate compose), creds `1mTheSenatePalp4tine` / `DarkTr00per_66` | `CTF{D34TH_ST4R_PL4NS}` |

- **#12 —** *"Not even an Emperor, full control of his own machine has.
  Somewhere, a picture, more than it shows, hides."*
  **Hint:** The Death Star capstone credentials also work over SSH. Once
  in, check what you're allowed to run as root without a password.

## Why these levels

- **Level 0** — view-source / HTML-comment / a JS `confirm()` trap. No
  terminal, no technique, purely "look closer". Matches the doc's Level 0
  bar exactly (`view source` is the given Web example).
- **Level 1** — requires poking at a specific tool/endpoint (enumerating
  ImperialNet profiles by guessing/URL-formatting names, following the BAC
  chain to reach the Skywalker page, spoofing a header on the login page)
  but no named vulnerability class yet.
- **Level 2** — one clean, textbook vulnerability each: a stored-XSS
  **filter bypass** (a single-pass sanitiser defeated by splitting the
  payload), broken access control (reaching the panel), an **IDOR** (reading a
  record you shouldn't, #8), and weak-credential guessing at `/BruteForce`.
- **Level 3** — chains that can't be solved by pasting one generic payload:
  the Dark Holocron login needs an injection *targeted* at an account whose
  name must first be **enumerated through the injection itself** (a plain
  `' OR 1=1 -- ` lands on the wrong user and earns nothing here), and the
  Death Star flag needs a **real dictionary attack** against the admin login
  (a provided leak dump, the obvious guesses seeded as decoys), and is only
  reachable after chaining BAC → SQLi → brute force → admin login across the
  whole app (the doc's "first level with multiple layers"). Note there is no
  "three escalating SQL injection
  steps" anywhere in the app — earlier versions of this file and of
  `rebel/index.html` claimed that; it was never true, it's a single form.
- **Level 4 (bonus, #12)** — the first challenge outside Web Security:
  shell access, privilege escalation, forensics tooling. A completely
  different skill set from the rest of the app, explicitly optional so it
  doesn't threaten the 2h budget for players doing the core 11. Not part of
  the required chain — no other flag depends on it. Delivered via
  `vulnbox/` (separate Docker image, `docker-compose.bonus.yml`, a single
  container) - SSH in with the reused capstone credentials, `sudo
  -l` reveals a GTFOBins-exploitable `find` entry, escalate to root, find
  `deathstarSeecret.jpg` and extract the steganographic flag. Full chain
  verified end-to-end with real `ssh`/`sshpass`, see `SOLUTIONS.md` #12.
- **#14 (easter egg)** — `/imperialnet/login` was previously a dead,
  disabled-form endpoint reachable from every ImperialNet page's nav bar.
  It now trusts a client-supplied `X-Forwarded-For` header to decide
  whether the request "comes from Imperial territory" - a realistic,
  common real-world flaw (trusting a spoofable header for network-origin
  access control instead of a validated proxy chain) not otherwise covered
  by the other 13 flags. Entirely optional, no other flag depends on it.

## Balance checklist (section 8 of the guide)

- [x] Every challenge has a category and level.
- [x] Point values follow the section-3 table for each level.
- [x] **Counts:** 11 required flags (#1-#11), 1 bonus (#12) and 2 easter eggs
      (#13, #14) = **14 total**. Required path is worth **2150 pts**; with
      the bonus and both easter eggs, **2800**.
- [x] Distribution skews toward L0-L2 (9 of 11 required), with L3 reserved for
      the targeted SQLi and the capstone. The shape is a ramp into one hard
      chain, not a statement about the audience: difficulty is calibrated
      against a player working with an AI assistant open (see the note under
      #10), so the L0-L2 band is deliberately quick to clear rather than
      padded out.
- [x] Hints are baked into the story text (generous at the low end, the
      SQLi/brute-force chain expects the player to have taken notes; #7's
      candidate wordlist is linked from `/ImperialWebscraper`, matching a
      real dictionary-attack workflow instead of a flat view-source answer)
      and now also spelled out per-flag above (spoiler-free description +
      a more concrete hint).
- [x] Writeups: see `SOLUTIONS.md` — every flag traced and verified against
      the live app, including exact payloads.
- [x] Flags are one consistent format: `CTF{...}`, case-sensitive.
- [x] All 11 required flags are reachable in-game (two gaps found while
      writing `SOLUTIONS.md` — #11/enumeration and the SQLi-only Admin1
      flag — were wired up rather than left dead; #13/patience and
      #14/login-bypass added later as pure easter eggs, no gap to fix).
- [x] **No flag is reachable below its own level** (2026-08-06 review):
      #10 (L3) used to be readable by typing `/darkholocron/Admin1` with no
      injection at all, and #7's two keywords (L2) sat on pages open from
      the first second. Both now require the progress their level implies —
      the sith page stays open for the L0 trap, but its intel doesn't.
- [x] Bonus flag #12 is announced on `/` and fully reachable end-to-end via
      `vulnbox/` — verified with real SSH, not just inspected in the
      Dockerfile.
