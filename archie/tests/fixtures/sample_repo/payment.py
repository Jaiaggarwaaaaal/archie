"""Payment processing module."""
from .validators import validate_card, validate_amount


class PaymentService:
    """Handles payment operations."""
    
    def __init__(self, api_key):
        self.api_key = api_key
    
    def process_payment(self, amount, card):
        """Process a payment transaction."""
        validate_amount(amount)
        validate_card(card)
        # BUG: Missing null check on card.token
        return self._charge(card.token, amount)
    
    def _charge(self, token, amount):
        """Internal charge method."""
        return {"status": "success", "amount": amount}
    
    def refund(self, transaction_id):
        """Refund a transaction."""
        return {"status": "refunded", "id": transaction_id}
