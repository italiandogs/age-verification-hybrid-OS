import stripe
from datetime import datetime, timezone
from user_data_handling import get_user_by_discord_id, update_user_verification_status, set_verification_attempt

# Stripe setup (use your restricted key)
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

def create_stripe_verification_session(discord_id, role_id):
    """Generates a verification link using Stripe's verification service."""
    try:
        verification_session = stripe.identity.VerificationSession.create(
            type='document',
            metadata={
                'discord_id': discord_id,  # Only Discord ID is passed in metadata
                'role_id': role_id
            },
            options={
                'document': {
                    'require_id_number': False,
                    'require_live_capture': True,
                    'require_matching_selfie': True
                }
            }
        )
        return verification_session.url
    except stripe.error.StripeError as e:
        print(f"Stripe error: {e}")
        return None

def handle_stripe_verification_result(session_id):
    """Handles the result from Stripe after verification."""
    session = stripe.identity.VerificationSession.retrieve(session_id)
    
    # Get discord_id from the session metadata
    discord_id = session.metadata.get('discord_id')
    
    # Extract verified Date of Birth (dob)
    dob = session.verified_outputs['dob']

    # Update the user verification status
    update_user_verification_status(discord_id, status=True)
    
    # Log the verification attempt
    set_verification_attempt(discord_id)
    
    print(f"User {discord_id} has been verified.")
