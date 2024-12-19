from werkzeug.security import generate_password_hash

password = 'admin'
hashed_password = generate_password_hash('password123', method='pbkdf2:sha256')
print(hashed_password)