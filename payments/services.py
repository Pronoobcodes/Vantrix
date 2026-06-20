import requests
from django.conf import settings

class PaystackService:

    BASE_URL = "https://api.paystack.co"

    @classmethod
    def initialize_payment(cls, email, amount, reference, callback_url):
        url = f"{cls.BASE_URL}/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "email": email,
            "amount": int(amount * 100),  # Paystack expects amount in kobo
            "reference": reference,
            "callback_url": callback_url
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            response.raise_for_status()
        except requests.RequestException:
            return None

        return response.json()
        
    @classmethod
    def verify_payment(cls, reference):
        url = f"{cls.BASE_URL}/transaction/verify/{reference}"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
        except requests.RequestException:
            return None

        return response.json()