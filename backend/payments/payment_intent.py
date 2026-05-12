from stripe import StripeClient
from django.conf import settings

client = StripeClient(settings.STRIPE_SECRET_KEY)

def create_payment_intent(amount, currency, user_id):
    print(f"Using key: {settings.STRIPE_SECRET_KEY}")
    payment_intent = client.v1.payment_intents.create({
        "amount": amount,
        "currency": currency,
        'automatic_payment_methods': {'enabled': True, "allow_redirects": "never"},
        "metadata": {'user_id': user_id},
    })

    return payment_intent
