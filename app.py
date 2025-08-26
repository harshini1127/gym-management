from werkzeug.security import generate_password_hash, check_password_hash

# When registering:
hashed_password = generate_password_hash(password)
cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))

# When logging in:
cursor.execute("SELECT password FROM users WHERE username=%s", (username,))
row = cursor.fetchone()
if row and check_password_hash(row[0], password):
    # success
