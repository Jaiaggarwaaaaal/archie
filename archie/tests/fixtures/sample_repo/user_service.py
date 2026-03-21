"""User management service."""
from .validators import validate_email


class UserService:
    """Manages user operations."""
    
    def create_user(self, email, name):
        """Create a new user."""
        validate_email(email)
        return {"email": email, "name": name}
    
    def get_user(self, user_id):
        """Retrieve user by ID."""
        return {"id": user_id}
    
    def validate_email(self, email):
        """Duplicate: validates email - same as validators.py."""
        if "@" not in email:
            raise ValueError("Invalid email")
        return True
