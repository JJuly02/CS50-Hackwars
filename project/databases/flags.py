from cs50 import SQL
from werkzeug.security import generate_password_hash

# Inicjalizacja połączenia z bazą danych
db = SQL("sqlite:///users.db")

# Nowe flagi do dodania
flags = [
    "no flags for you :p but nice try nevertheless"
    "however on the second thought... "
    "49 4d 50 2d 52 33 44 53 34 42 33 52"
]

# Czyszczenie tabeli validflags
db.execute("DELETE FROM validflags")

# Dodawanie nowych flag z hashowaniem
for flag in flags:
    hashed_flag = generate_password_hash(flag, method='pbkdf2:sha256', salt_length=8)
    db.execute("INSERT INTO validflags (flag) VALUES (:flag)", flag=hashed_flag)
