from security import get_password_hash, verify_password, create_access_token

# 1. Test bcrypt hashing
hashed = get_password_hash("mfg_secret_2026")
print(f"Bcrypt hash: {hashed[:40]}...")
print(f"Verify correct password: {verify_password('mfg_secret_2026', hashed)}")
print(f"Verify wrong password: {verify_password('wrong_password', hashed)}")

# 2. Test JWT generation
token = create_access_token(user_id=1)
print(f"JWT token: {token[:50]}...")

# 3. Decode and verify payload structure
import jwt
payload = jwt.decode(token, "meditrace-jwt-secret-change-in-production", algorithms=["HS256"])
print(f"Decoded payload: {payload}")
print(f"Contains role? {'role' in payload}")
print(f"Contains sub? {'sub' in payload}")
print(f"Contains exp? {'exp' in payload}")
