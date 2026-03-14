import random
import string
from passlib.context import CryptContext


class SecurityUtils:
    _instance = None
    _pwd_context = None

    # Singleton
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SecurityUtils, cls).__new__(cls)
            cls._pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return cls._instance

    @staticmethod
    def hash_password(password: str) -> str:
        """hash the password passed as a parameter.

        Args:
            password (str): The password to hash.

        Returns:
            str: The hashed password.
        """
        # S'assurer que le singleton est instancié
        # Ensure singleton is instantiated
        if SecurityUtils._pwd_context is None:
            SecurityUtils()
    
        # Debugging: Log original password length
        print(f"Original password length: {len(password)}")
    
        # Truncate password if longer than 72 bytes
        if len(password) > 72:
            password = password[:72]
            print("Password truncated to 72 bytes.")
    
        return SecurityUtils._pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        """Verify if the password matches the hashed password.

        Args:
            plain (str): The plain password to verify.
            hashed (str): The hashed password to compare against.

        Returns:
            bool: True if the passwords match, False otherwise.
        """
        # S'assurer que le singleton est instancié
        if SecurityUtils._pwd_context is None:
            SecurityUtils()
        return SecurityUtils._pwd_context.verify(plain, hashed)

    def generate_random_password(length: int = 12) -> str:
        """Generate a random password.

        Args:
            length (int, optional): The length of the password to generate. Defaults to 12.

        Returns:
            str: A randomly generated password.
        """
        characters = string.ascii_letters + string.digits + string.punctuation
        return "".join(random.choice(characters) for _ in range(length))
