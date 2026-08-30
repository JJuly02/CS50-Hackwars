# Solutions / Writeups

**Spoiler warning.** This is the official maintainer writeup for every flag in
`CHALLENGES.md` — for organizers/instructors, not for players. Traced directly
against the current `app.py`/templates, not the story text, so a couple of
things below don't match the in-game narrative (noted where relevant).
11 required flags (#1-#11) plus 1 bonus (#12, built and verified via a
separate `vulnbox/` Docker image) plus 2 pure easter eggs (#13, patience;
#14, ImperialNet login header spoofing) — 14 in total. The numbering in this
file is canonical; `CHALLENGES.md` was realigned to it on 2026-08-06 and
`ctfd/challenges.yml` carries it in per-entry comments.

No accounts, no login — CTFd handles auth and flag submission. This app just
gives every visitor an anonymous per-browser session (holocronstage/
archivestage in a signed cookie) so the story's sequential unlocks still
work without a rebel account.

---

## 1. `CTF{R3B3L10N}` — View Source Easter Egg

- **Where:** `/` (Rebel index).
- **Solve:** Open `/`, View Page Source, find the HTML comment near
  the bottom of the body: `<!-- CTF{R3B3L10N} -->`.

## 2. `CTF{1MP3R1AL}` — ImperialNet Comment Leak

- **Where:** `/imperialnet` (no login required — this zone is public).
- **Solve:** View Page Source, find the comment near the bottom:
  `<!-- CTF{1OR3T1CN} -->`. The `CTF{...}` shell looks exactly like every
  other flag's format — that's the trap. Submitting it as-is gets rejected;
  only the letters *inside* the braces are Caesar-shifted by **+2**
  (`CTF{` and `}` are untouched, already correct). Shift `1OR3T1CN` back
  by 2 to get `1MP3R1AL`, giving the real flag `CTF{1MP3R1AL}`. Blindly
  shifting the whole comment (prefix included) produces `AZ26{1MP3R1AL}` -
  wrong, and a clue that the prefix wasn't part of the cipher.

## 3. `CTF{17S_4_TR4P}` — The Trap

- **Where:** `/darkholocron/darkholocron/secretmessage` (dark/troll.html).
- **Solve:** No progress needed — `login_holo(0)` checks `holostage < 0`,
  which is never true, so this route (and `/sith` below) is open to anyone.
  The discovery path: View Page Source on `/darkholocron` (the login form,
  dark/mlogin.html) — there's a "TODO" dev-note comment mentioning
  `/darkholocron/sith` is linked but shouldn't be public yet. Visit
  `/darkholocron/sith` directly, click "Unearth More Secrets" →
  `/darkholocron/darkholocron/secretmessage`. A JS `confirm()` shows the
  flag text, then redirects to a YouTube rickroll on OK.

## 4. `CTF{PH4NT0MMEN4C3}` — Skywalker Chronicles

- **Where:** `/darkholocron/skywalker` (dark/skywalker.html), gated by
  `@holo_stage_required(1)`.
- **Solve:** Unlike #3, this one does require the BAC chain: submit any
  SQLi payload that returns a row at `/darkholocron` (e.g. `' OR 1=1 -- `)
  to reach `holocronstage = 1`, then visit `/darkholocron/skywalker`
  directly. The flag is plain text on the page (dark text on a dark
  background — it's meant to blend in, not be invisible; select-all or
  view-source both work).

## 5. `CTF{IMP3R1ALXSS}` — Stored XSS in Comments (filter bypass)

- **Where:** `/imperialnet/comments`. What survives the input filter is
  rendered with Jinja's `| safe`, so a payload the filter does *not*
  neutralise executes for real, for every visitor (genuine stored XSS).
- **The filter (2026-08-09):** `sanitize_comment()` in `helper.py` strips
  `<script>` tags, `on*=` event handlers and `javascript:` URIs — but in a
  **single pass with no re-scan**. Both storage and the flag check run on the
  *sanitised* text, so a naive `<script>alert(1)</script>` is stripped to
  `alert(1)` and scores nothing. That is the challenge now; before this date
  there was no filter and a bare script tag scored on the first try.
- **Solve — split the token so it reassembles after one removal:**
  - `<scr<script>ipt>alert(1)</scr</script>ipt>` → the inner `<script>` /
    `</script>` are removed, the outer halves close up into a working
    `<script>alert(1)</script>`.
  - `<img src=x oonerror=nerror=alert(1)>` → the `onerror=` in the middle is
    removed, leaving `<img src=x onerror=alert(1)>`.
  A red banner with `CTF{IMP3R1ALXSS}` appears under any comment whose
  *stored* form still contains executable markup — so only a real bypass
  scores. A bare `<img>`/`<svg>` with no handler does not (it is not XSS).
- **Operational note:** the comment list is a plain in-process list shared by
  everyone on that team's instance, so a payload like
  `<script>window.location=...</script>` hijacks the page for the whole team.
  It's capped at 20 player comments (oldest drop off, the 3 seeded ones
  stay), so such a payload eventually scrolls off — but the fast fix during
  an event is `docker compose restart teamN`, which clears the list entirely.

## 6. `CTF{BROK3NKONTROL}` — Broken Access Control: Admin Panel

- **Where:** `/darkholocron/admin`.
- **Solve:**
  1. Submit a SQLi payload that returns any row at `/darkholocron`,
     e.g. username `' OR 1=1 -- ` (password anything). The query takes the
     first matching row (`DarthVader`), which sets your session's
     `holocronstage` to 1 and redirects you to `/darkholocron/DarthVader`.
  2. That page now links directly to `/darkholocron/admin` ("Admin Control
     Panel", with a wink that a mere login shouldn't open it) — click it,
     or navigate there directly. The route's "you shouldn't be able to see
     this" branch fires and shows
     `Broken access control - CTF{BROK3NKONTROL}`.
- **Fixed:** this used to depend on a process-global `Holoload` class
  attribute shared by every player on the server; it's now gated purely by
  your own session, so it reliably shows the first time each visitor reaches
  the panel, regardless of what anyone else has done.
- **Fixed (2026-08-09):** the flag was emitted only when `holocronstage` was
  exactly 1, so a player who opened with the *targeted* `Admin1` injection
  (#10) — which jumps the session straight to stage 2 — never saw it, on any
  visit, with no error and no way back short of clearing cookies. Solving the
  harder Level 3 challenge first silently cost 250 pts. The award now fires on
  first arrival at the panel whichever injection got you in, tracked on its own
  `bac_admin_panel` session key so it stays one-shot.

## 7. `CTF{4CC3SS_6R4N73D}` — Weak Credentials Brute Force

> **Redesign pending.** This challenge's mechanic (two "keywords", either
> order) doesn't model any real attack, and the app already contains a real
> credential-guessing target at `/darkarchive/adminlogin`. A redesign is
> possible; what's described below is what currently ships.

- **Where:** `/BruteForce`, unlocks `/darkarchive`.
- **The 9 curated `/ImperialWebscraper` keywords are a decoy** — the real
  two words aren't in that shortlist. The page itself links to
  `static/rockyouWars.txt`, framed as "the scraper's raw, unfiltered dump" -
  30 Star-Wars-flavored candidate words/passwords, including both real
  answers (`SithCode`, `4Empire`) mixed in with decoys (`Vader66`,
  `Order66!`, `MayThe4th`, etc.). With 30 words that's `C(30,2) = 435`
  unordered pairs - tedious by hand, realistic to brute force with a small
  script (e.g. Python + `requests`, looping pairs from the wordlist against
  `/BruteForce` until one redirects with success). No rate limiting on this
  route, so it's fast.
  - They're also still planted as styled (bold, red) easter eggs on two
    pages, as a redundant fallback for players who get stuck without ever
    finding the wordlist:
    - `SithCode` — on `/darkholocron/sith`, but **only once
      `holocronstage >= 1`** (i.e. after any successful SQLi login). The page
      itself stays open to everyone because it's the discovery path to #3's
      trap; at stage 0 the same section renders as "The Code of the Sith"
      with no highlighted keyword. Before the 2026-08-06 review this word
      was readable by anyone on their first page load, which made the whole
      Level 2 challenge skippable from a standing start.
    - `4Empire` — visible on Darth Vader's ImperialNet profile,
      `/imperialnet/Darth-Vader` (shown because `isvader == True`). Left
      ungated: one word of the pair on its own doesn't open anything.
- **Solve:** Submit `keyword1=SithCode`, `keyword2=4Empire` (either order
  works) at `/BruteForce`. This sets `archivestage = 1` and redirects to the
  animation page. Then open `/darkarchive` — the flag pops up immediately
  via `alert("CTF{4CC3SS_6R4N73D}")`.

## 8. `CTF{4DM1NCON7R0L}` — Death Star Access Code (IDOR)

- **Where:** the admin panel's "Akta Personalne" (personnel record) viewer,
  `/darkholocron/admin?uid=<id>`.
- **Redesigned (2026-08-09):** the access code used to sit in the panel body
  unconditionally, so #6 and #8 both landed on one page load — 500 pts for a
  single click (and the harder-first player could still miss #6). It is now
  behind an **IDOR**. The record viewer reads the `uid` query parameter and
  does no ownership check; it defaults to the current admin's own record
  (`uid=5`, "This is you") and trusts whatever id the client asks for.
- **Solve:**
  1. Reach the panel (#6's step: any SQLi login, then `/darkholocron/admin`).
     It shows your own record and a `?uid=` in the URL.
  2. Step the id onto a record that isn't yours. `uid=6` is the Emperor's
     record, whose note reads
     `Death Star access code: CTF{4DM1NCON7R0L}`.
- **What it does not leak:** records come from a curated dict in `app.py`
  (`ADMIN_RECORDS`), not the holocron auth table, so no password material is
  exposed by walking the ids; only the Emperor's record carries a flag.

## 8b. Design note — why the split

#6 (reaching the panel at all) and #8 (reading a record you shouldn't) are now
two distinct actions on two distinct vulnerability classes (broken access
control vs. IDOR), instead of one page view paying out twice.

## 9. `CTF{M4Y_7H3_F0RC3_B3_W17HY0}` — Death Star Capstone

- **Where:** `/darkarchive/admin`.
- **Intended solve:**
  1. Complete #7 (`archivestage = 1`).
  2. `/darkarchive` ("Recovered Intelligence") gives the username
     `1mTheSenatePalp4tine` and links a leaked password dump,
     `static/imperial_creds_leak.txt`.
  3. Run that list against `/darkarchive/adminlogin` (username fixed, password
     from the list). The match is `DarkTr00per_66`, at line ~106 of 151.
     Success sets `archivestage = 2` and redirects to `/darkarchive/admin`,
     which fires `alert("CTF{M4Y_7H3_F0RC3_B3_W17HY0}")`.
- **Redesigned (2026-08-09):** the password used to be `Admin123!` with an
  in-game "rockyou.txt is a nice file ;)" nudge — a top-of-mind guess that an
  AI assistant produces in its first few tries, so the "dictionary attack" was
  decorative. It is now `DarkTr00per_66`: themed and in the provided dump, but
  not an obvious guess. The obvious guesses (`Admin123!`, `Password1`, `admin`,
  `P@ssw0rd`…) are planted in the same list as **non-matching decoys**, so a
  naive attempt returns "Access denied" and the intended solve is genuinely
  running the list. There is **no lockout and no per-attempt delay** — the
  `time.sleep(1)` in `app.py` fires only on success (a failure-side sleep would
  pin a thread on single-worker gunicorn and let a player's own script DoS
  their team's box). The cost that makes it an exercise is list length, not
  throttling.
- **Note:** this password is reused as the SSH password for the bonus vulnbox
  (#12). Change one → change both (`vulnbox/Dockerfile`) and rebuild the image.
- **Fixed earlier:** `/darkarchive/admin` requires `archive_stage_required(2)`
  — the admin-login step is mandatory, no shortcut via brute force alone.

## 10. `CTF{4DM1NP4N3L}` — Dark Holocron Admin1 Access

- **Where:** `/darkholocron/Admin1` (dark/holocron.html, `is_admin1` branch).
- **Hint (rewritten 2026-08-09):** `/darkholocron/sith` ("Whispers from the
  Archives") no longer names the account. It now says a privileged system
  account exists whose name appears on no roster, that the login redirects you
  addressed by the name it matched, and that resolving the query to one account
  after another and reading each redirect reveals the name. The name `Admin1`
  used to be printed there outright, which reduced "targeted SQLi" to typing a
  handed-over string — see the enumeration step below. That section is gated
  behind `holocronstage >= 1` — see #7.
- **Gating (fixed 2026-08-06):** the flag renders only when
  `session["sqli_admin1"]` is set, which happens in exactly one place: the
  branch of `/darkholocron`'s POST handler where the injected query resolved
  to the `Admin1` row. Previously the template keyed off the URL alone, so
  typing `/darkholocron/Admin1` — a name the sith page hands out — returned
  a Level 3 flag with no injection at all. Note it can't key off
  `holocronstage >= 2` either: the broken-access-control challenge (#6) also
  pushes the stage to 2, which would have re-opened the same shortcut one
  step later.
- **Enumerate the name first (2026-08-09):** the login redirects to
  `/darkholocron/<matched username>`, which leaks the name of whatever row the
  query resolved to. So iterate the injection across rows and read the redirect
  target: `' OR 1=1 LIMIT 1 OFFSET 0 -- ` → `DarthVader`, `OFFSET 4` →
  `Admin1`, etc. (or `' OR username LIKE 'A%' -- ` and vary the letters). The
  privileged account surfaces as `Admin1`.
- **Solve:** Once you know the name, log in with a payload that resolves to the
  `Admin1` row specifically — e.g. username `Admin1' -- ` (password anything;
  the comment strips the password check). This differs from the generic
  `' OR 1=1 -- ` used in #6/#8, which returns the first row (`DarthVader`),
  because the app only ever reads `query[0]` — landing on `Admin1` requires the
  injection to match *only* that username. Sets `holocronstage = 2` and
  `sqli_admin1`, redirects to `/darkholocron/Admin1`, page shows
  `CTF{4DM1NP4N3L}` directly.

## 11. `CTF{R3DS4B3R}` — ImperialNet Profile Enumeration

- **Where:** `/imperialnet/Grand-Inquisitor` — a profile that exists in
  `imperialnet.db` (id 6) but is **not linked anywhere** on `/imperialnet`
  (only the original five leaders have cards there).
- **Solve:** Two independent leads point here, so it's findable without
  needing both: (1) the "Inquisitors" mention on `/darkarchive` ("The
  Inquisitors: Hunters of the Jedi"), nudging you to try enumerating
  profiles beyond the five listed; (2) `/robots.txt` has a
  `Disallow: /imperialnet/Tenaq-Vadhvfvgbe` entry — classic "hiding" a path
  in robots.txt while announcing it exists. That slug is ROT13; decode it
  to get `Grand-Inquisitor`. Either way, visit
  `/imperialnet/Grand-Inquisitor` (case-insensitive, dash-for-space, same
  convention as every other profile URL). The flag is shown directly on the
  page.

## 12. `CTF{D34TH_ST4R_PL4NS}` — Death Star Plans (bonus)

- **Where:** `vulnbox/` — a separate Docker image (`docker-compose.bonus.yml`
  at the repo root, independent of the main app's compose file), a single
  container with SSH on port 2201 locally. SSH only, no web component.
- **Framing:** after #9's capstone, the same reused credentials
  (`1mTheSenatePalp4tine` / `DarkTr00per_66`) also work over SSH to Palpatine's
  personal machine. Low-priv shell only - "not even the Emperor has root on
  his own laptop, Imperial IT policy."
- **Solve (verified end-to-end with `sshpass`, not just read from the
  Dockerfile):**
  1. `ssh 1mTheSenatePalp4tine@<host> -p <team's port>`, password
     `DarkTr00per_66`.
  2. `sudo -l` shows: `(root) NOPASSWD: /usr/bin/find` - a classic
     [GTFOBins](https://gtfobins.github.io/gtfobins/find/) entry.
  3. `sudo find . -exec /bin/sh \; -quit` (interactive session) spawns a
     root shell. Confirmed non-interactively too: `sudo find . -exec
     whoami \;` prints `root`.
  4. `deathstarSeecret.jpg` sits at `/root/deathstarSeecret.jpg`, mode
     `600`, owned by root - unreadable until step 3. Copy it out (e.g.
     `cp`/`scp` after making it readable, or just `cat` it through the root
     shell and redirect to a local file) and follow #12's own extraction
     steps below.
- **Isolation:** each team's container is fully independent (own
  filesystem, own root, own everything) - one team rooting their box has
  zero effect on any other team's.
- **Where the flag artifact itself lives:** `deathstarSeecret.jpg` at the
  repo root. It's a real, visually-untouched JPEG (a "DS-1 Orbital Battle
  Station" schematic) with a Base64-encoded payload appended **after** the
  real JPEG EOF marker (`FF D9`). Any image viewer stops reading at the EOF
  marker and shows the schematic normally - the flag data is only visible
  by inspecting the raw file.
- **Why append-after-EOF instead of "real" LSB/`steghide`:** JPEG is a lossy
  format, so classic LSB-in-pixel steganography doesn't survive being
  re-saved as a .jpg regardless of tool - the compression step perturbs the
  bits you hid. Genuine JPEG-domain tools (`steghide`, DCT-coefficient
  editing via `jpegio`) would need a working install of one of those, which
  wasn't reliably buildable in this environment (`steghide` isn't in
  homebrew-core; `jpegio` failed to compile). Data-after-EOF is the one
  approach that's guaranteed not to corrupt the image and needs no special
  tooling on either side - a well-established file-carving technique, if
  not textbook LSB steganography.
- **Extracting the flag once you have the file:**
  1. Notice the file is larger than a normal JPEG for its dimensions, or
     just inspect it: `file deathstarSeecret.jpg` still reports a clean
     JPEG, but `strings deathstarSeecret.jpg | tail` (or `binwalk`, or a hex
     viewer) shows `--BEGIN-CLASSIFIED--` / `--END-CLASSIFIED--` markers
     after the point where legitimate JPEG data ends.
  2. Extract the Base64 blob between those markers and decode it:
     ```python
     import base64
     data = open("deathstarSeecret.jpg", "rb").read()
     start = data.find(b"--BEGIN-CLASSIFIED--") + len(b"--BEGIN-CLASSIFIED--")
     end = data.find(b"--END-CLASSIFIED--")
     print(base64.b64decode(data[start:end].strip()).decode())
     ```
     Prints `CTF{D34TH_ST4R_PL4NS}` (plus two lines of flavor text). The
     flag isn't findable via a plain `strings | grep CTF` - it's Base64,
     not plaintext, so the marker strings are the actual thing to notice.
- **Safety:** the payload is appended after the JPEG's end-of-image marker,
  so the image itself is untouched - `file` still reports a clean JPEG and
  the decoded pixels are bit-for-bit identical to the original; only trailing
  bytes were added.

## 13. `CTF{P4T13NC3_YOUNG_P4DAW4N}` — Patience Easter Egg

- **Where:** `/` (Rebel index), at the very end of the Star Wars opening
  crawl text.
- **Solve:** Either wait out the full 150s crawl animation
  (`.crawl-content`'s CSS animation) until it scrolls past "May the Secure
  Code be with you..." to the final lines, or just View Page Source /
  scroll the underlying div - the flag is plain text, no gating, same
  Level 0 convention as #1. Pure reward for reading to the end, not tied to
  any technique.

## 14. `CTF{TRUST_NO_H34D3R}` — ImperialNet Login Header Spoofing (easter egg)

- **Where:** `/imperialnet/login` (linked in the nav bar on every ImperialNet
  page — `imperiallogin.html`). Previously a fully dead, disabled-form
  endpoint left over from the removed account system.
- **The flaw:** the route decides whether the request "comes from Imperial
  territory" by reading `X-Forwarded-For` directly off the request and
  checking whether the first IP in it starts with `10.66.6.` — a
  client-supplied header, trusted with no validated reverse-proxy chain in
  front of it. A completely standard, real-world flaw (trusting spoofable
  headers for network-origin access control) not otherwise represented in
  this app's 13 other flags.
- **Solve:**
  1. View source on `/imperialnet/login` — a dev-note HTML comment
     ("temporary VLAN check via X-Forwarded-For... Imperial internal range
     is 10.66.6.0/24") gives away both the mechanism and the exact subnet.
  2. Send any request to `/imperialnet/login` with a spoofed header, e.g.
     `curl -H "X-Forwarded-For: 10.66.6.1" http://<host>/imperialnet/login`
     (or a browser extension that sets custom headers). The page renders a
     green "Imperial network verified" banner with the flag instead of the
     usual "You cannot login from outside..." warning. A comma-separated
     chain works too — only the first entry is looked at, which is itself
     part of the lesson.
- **Accepted values:** the first entry has to parse as a real address inside
  `10.66.6.0/24` (`ipaddress` module, not a string prefix). Until
  2026-08-06 the check was `startswith("10.66.6.")`, which also accepted
  nonsense like `10.66.6.66666` — a sloppier bug than the one being taught.
- **Why an easter egg, not required:** purely additive — no other flag
  depends on it, and it doesn't touch the main story's sequential unlocks.
  Added to make an otherwise-empty, always-visible nav-bar link
  interactive instead of a dead end.

---

## Notes for the challenge author

- **Review pass** (a full list of findings tracked separately, including what
  was deliberately *not* changed). Two of the findings were solve-integrity
  bugs and are fixed here: #10 was readable
  by URL alone (details under #10 above) and #7's keywords were public from
  the first page load (details under #7). Also fixed: two 500s on POSTs with
  a missing form field (`/imperialnet/comments`, `/BruteForce` — the latter
  matters because #7 is the one challenge players are expected to script),
  an unbounded comments list, and the too-loose `X-Forwarded-For` prefix
  match. All re-verified against a running instance, including that #3's
  Level 0 trap is still reachable with zero progress.
- All 11 required flags are reachable and have been re-verified end-to-end
  against the live app after these fixes. #12 (bonus) and #13 (easter egg)
  came later - both are now fully live: #12's `vulnbox/` was built and the
  entire SSH → `sudo -l` → GTFOBins → root → flag chain verified with real
  `ssh`/`sshpass`, not just inspected in the Dockerfile.
- **#11's** hidden profile is new content added during this pass — it
  reuses the already-established "Inquisitors" lore from `/darkarchive`.
  Feel free to reskin if you want different flavor text.
- Two correctness bugs turned up while re-verifying every path end-to-end and
  are now fixed: `apology()`'s themed "Error Code" (40-48, 66) was being sent
  as the literal HTTP status, which is invalid HTTP/1.1 for anything under
  100 and gets dropped by strict clients/proxies (confirmed with curl); and
  `/BruteForce`/`/BruteForce/animation` read the session without a login
  check, so visiting either with no prior state crashed with a raw 500.
  Both would have hit real players during a live event.
- A full code review + smoke-test pass afterward found and fixed several
  more things: sessions are now Flask's default signed cookie instead of a
  server-side filesystem store (no more per-request disk I/O, no scaling
  concern across multiple instances, and no `SECRET_KEY`-unset
  warning going unnoticed - the app now prints one loudly on startup);
  resubmitting correct `/BruteForce` keywords after already finishing
  `/darkarchive/adminlogin` used to silently downgrade `archivestage` back
  to 1, locking the capstone until adminlogin was redone - fixed to never
  downgrade; `/darkholocron/skywalker` used to be reachable with zero
  prior steps (the same `login_holo(0)` no-op as #3's trap) - it now
  requires `holocronstage >= 1` (the BAC chain), matching its Level 1
  billing in `CHALLENGES.md`; and the repeated `login_holo`/`login_archive`
  + `apology(...)` guard blocks across 8 routes were collapsed into two
  decorators (`holo_stage_required`/`archive_stage_required`).
- The rebel login/register/logout/score system has been removed (CTFd now
  owns auth and flag submission). Sequential unlocks (`holocronstage`/
  `archivestage`) still work, but as an anonymous per-browser session
  instead of a `users.db` account — no registration step anywhere anymore.
  A third crash bug was found and fixed in this same pass: submitting wrong
  credentials to `/darkarchive/adminlogin` fell through with no `return`,
  crashing with a 500 instead of showing an error.
- **Playtest round** (first real human run-through) surfaced several
  discoverability gaps, now fixed: #5's flag was only reachable via a
  narrow server-side regex on `<script>` tags and revealed as an invisible
  HTML comment. First replaced with a cookie-based reveal (any working XSS
  vector reads `document.cookie` and writes it to the page) - but that
  turned out to be *more* confusing in practice (easy to test with `alert()`
  out of habit and see nothing happen, or mistype a closing tag and break
  the page). Settled on: broaden `detect_xss_payload()` to catch
  `<script>`, `on\w+=` handlers, `<svg>`, `<img>`, `<iframe>`,
  `javascript:` - not just a literal `<script>` match - and show a visible
  red banner with the flag directly under *that* comment (tracked
  per-comment now, not as one global flag applying to every card in the
  list, which was also a latent bug in the original version); #3's trap had
  no discovery path at all without already knowing the URL -
  added a dev-note comment on `/darkholocron`'s login page; #6's admin
  panel had no link anywhere, purely guessable - now linked directly from
  the post-SQLi landing page; #10 had zero in-game hint that `Admin1`
  exists - added one on `/darkholocron/sith`; #11 had only the
  `/darkarchive` lead - added a second, ROT13-obfuscated one via
  `robots.txt`.
- **#7 redesigned** after playtest feedback that it didn't feel like a
  brute force at all (just two words found via unrelated lore easter
  eggs): added `static/rockyouWars.txt`, a 30-word themed candidate list
  including both real answers, linked from `/ImperialWebscraper` as "the
  scraper's raw dump." Removed the plaintext answer that used to sit in an
  HTML comment on `/BruteForce`. The sith/Vader easter eggs stay as a
  redundant fallback.
- **`/` de-spoilered**: the four challenge-title cards used to literally
  name the vulnerability class ("Social Engineering", "XSS (Cross-Site
  Scripting)", "SQL Injection", "Broken Access Control") and the opening
  crawl repeated the same technique names in the story text. Both rewritten
  to describe *what's happening* narratively without naming the technique:
  "Loose Lips", "Whispers in the Wire", "The Sith Database", "Above Your
  Clearance". `ctfd/challenges.yml`'s challenge *names* still reveal
  technique in a couple of places (e.g. "Dark Holocron SQL Injection") -
  that's what players will actually see in CTFd's own challenge list on
  event day, so worth revisiting there too if the goal is no spoilers
  anywhere, not just on `/`.
- **#12 and #13 added** to `/`: a Level 4 (red) "Bonus" card for #12
  ("Beyond the Throne Room", non-revealing per the above) and #13's flag
  appended to the end of the opening crawl as a pure patience easter egg.
  Both also added to `databases/flags.py`/`flags.txt`/`ctfd/challenges.yml`
  for consistency (`databases/flags.py` seeds a `users.db` table the app no
  longer reads at runtime, but it's kept as the canonical flag list anyway).
- **#12's delivery built**: `vulnbox/Dockerfile` (Debian + sshd + the
  reused capstone credentials + a `sudo` NOPASSWD `find` entry) plus
  `docker-compose.bonus.yml`, separate from the main app's compose file since
  this is optional. Verified for real: SSH login, `sudo -l`, the GTFOBins
  escalation, extracting the root-owned image, and decoding the flag out of it.
