import razorpay
import stripe
from django.conf import settings
import logging
import uuid
import json

logger = logging.getLogger(__name__)

class PaymentGateway:
    """
    Payment Gateway wrapper that supports multiple payment providers
    """
    
    @staticmethod
    def get_gateway(provider='razorpay'):
        if provider.lower() == 'razorpay':
            return RazorpayGateway()
        elif provider.lower() == 'stripe':
            return StripeGateway()
        else:
            raise ValueError(f"Unsupported payment provider: {provider}")

class RazorpayGateway:
    """
    Razorpay payment gateway integration
    """
    
    def __init__(self):
        self.client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
    
    def create_order(self, amount, currency="INR", receipt=None):
        """
        Create a Razorpay order
        
        Args:
            amount: Amount in paise (1 INR = 100 paise)
            currency: Currency code (default: INR)
            receipt: Receipt ID (optional)
            
        Returns:
            dict: Order details including order_id
        """
        try:
            if not receipt:
                receipt = f"receipt_{uuid.uuid4().hex[:10]}"
                
            data = {
                "amount": int(amount * 100),  # Convert to paise
                "currency": currency,
                "receipt": receipt,
                "payment_capture": 1  # Auto-capture
            }
            
            order = self.client.order.create(data=data)
            return {
                'success': True,
                'order_id': order['id'],
                'amount': order['amount'] / 100,  # Convert back to rupees
                'currency': order['currency'],
                'provider': 'razorpay',
                'data': order
            }
        except Exception as e:
            logger.error(f"Razorpay order creation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_payment(self, payment_id, order_id, signature):
        """
        Verify Razorpay payment signature
        
        Args:
            payment_id: Razorpay payment ID
            order_id: Razorpay order ID
            signature: Razorpay signature
            
        Returns:
            bool: True if signature is valid, False otherwise
        """
        try:
            params_dict = {
                'razorpay_payment_id': payment_id,
                'razorpay_order_id': order_id,
                'razorpay_signature': signature
            }
            
            self.client.utility.verify_payment_signature(params_dict)
            return True
        except Exception as e:
            logger.error(f"Razorpay signature verification failed: {str(e)}")
            return False
    
    def get_payment_details(self, payment_id):
        """
        Get payment details from Razorpay
        
        Args:
            payment_id: Razorpay payment ID
            
        Returns:
            dict: Payment details
        """
        try:
            payment = self.client.payment.fetch(payment_id)
            return {
                'success': True,
                'data': payment
            }
        except Exception as e:
            logger.error(f"Failed to fetch payment details: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

class StripeGateway:
    """
    Stripe payment gateway integration
    """
    
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
    
    def create_payment_intent(self, amount, currency="inr", metadata=None):
        """
        Create a Stripe payment intent
        
        Args:
            amount: Amount in rupees
            currency: Currency code (default: inr)
            metadata: Additional metadata (optional)
            
        Returns:
            dict: Payment intent details
        """
        try:
            if not metadata:
                metadata = {}
                
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to smallest currency unit
                currency=currency,
                metadata=metadata,
                automatic_payment_methods={'enabled': True}
            )
            
            return {
                'success': True,
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id,
                'amount': intent.amount / 100,  # Convert back to rupees
                'currency': intent.currency,
                'provider': 'stripe',
                'data': intent
            }
        except Exception as e:
            logger.error(f"Stripe payment intent creation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def confirm_payment(self, payment_intent_id):
        """
        Confirm a Stripe payment
        
        Args:
            payment_intent_id: Stripe payment intent ID
            
        Returns:
            dict: Payment confirmation details
        """
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            return {
                'success': True,
                'status': intent.status,
                'data': intent
            }
        except Exception as e:
            logger.error(f"Stripe payment confirmation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

