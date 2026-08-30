from cs50 import SQL
from werkzeug.security import generate_password_hash

# Inicjalizacja połączenia z bazą danych
db = SQL("sqlite:///users.db")

# Flagi HackWars (format: CTF{...}), zgodne z ../flags.txt i ../CHALLENGES.md
flags = [
    "CTF{4DM1NP4N3L}",
    "CTF{BROK3NKONTROL}",
    "CTF{IMP3R1ALXSS}",
    "CTF{4CC3SS_6R4N73D}",
    "CTF{1MP3R1AL}",
    "CTF{M4Y_7H3_F0RC3_B3_W17HY0}",
    "CTF{PH4NT0MMEN4C3}",
    "CTF{17S_4_TR4P}",
    "CTF{R3DS4B3R}",
    "CTF{4DM1NCON7R0L}",
    "CTF{R3B3L10N}",
    "CTF{P4T13NC3_YOUNG_P4DAW4N}",
    "CTF{D34TH_ST4R_PL4NS}",
    "CTF{TRUST_NO_H34D3R}",
]

# Czyszczenie tabeli validflags
db.execute("DELETE FROM validflags")

# Dodawanie nowych flag z hashowaniem
for flag in flags:
    hashed_flag = generate_password_hash(flag, method='pbkdf2:sha256', salt_length=8)
    db.execute("INSERT INTO validflags (flag) VALUES (:flag)", flag=hashed_flag)
