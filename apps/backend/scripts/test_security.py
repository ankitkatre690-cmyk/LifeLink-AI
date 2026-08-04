from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)

password = "Ankit@2004"

hashed = hash_password(password)

print("Password:", password)
print("Hash:", hashed)
print("Verify:", verify_password(password, hashed))

token = create_access_token("123")

print("Token:", token)

print("Decoded:", decode_access_token(token))