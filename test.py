from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def test_hash(password):
    try:
        return pwd_context.hash(password)
    except Exception as e:
        print(f"Error: {e}")

print(test_hash("my_secure_password"))