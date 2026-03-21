"""Validation utilities."""


def validate_card(card):
    """Validate card details."""
    if not card:
        raise ValueError("Card is required")
    return True


def validate_amount(amount):
    """Validate payment amount."""
    if amount <= 0:
        raise ValueError("Amount must be positive")
    return True


def validate_email(email):
    """Validate email format."""
    if "@" not in email:
        raise ValueError("Invalid email")
    return True
