from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

hashed = pwd_context.hash("password123")
print(f"Hashed password: {hashed}")

assert pwd_context.verify("password123", hashed)
print("Password verification succeeded!")
