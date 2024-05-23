from cs50 import SQL
from werkzeug.security import generate_password_hash

# Connect to the database
db = SQL("sqlite:///palps.db")

# User credentials
key1 = "SithCode"
key2 = "4Empire"

# Hash the password
hashed_key1 = generate_password_hash(key1, method='pbkdf2:sha256', salt_length=8)
hashed_key2 = generate_password_hash(key2, method='pbkdf2:sha256', salt_length=8)

# Update the user in the database
db.execute("UPDATE users SET key1 = :key1, key2 = :key2 WHERE username = '1mTheSenatePalp4tine'", key1=hashed_key1, key2=hashed_key2)

print("User updated in the database.")
