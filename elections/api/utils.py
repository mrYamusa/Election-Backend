import random
import string

def generate_password():
    """Generate a random 12-character password"""
    return ''.join(random.choice(string.digits) for i in range(6))

def send_credentials_email(user_email, username, password):
    from django.core.mail import send_mail
    
    subject = f'Hi {username}, here\'s your Election Username and Password'
    message = f'''Hello!

Thank you for registering! Your voting account has been created successfully.

Username: {username}
Password: {password}

Please login to vote for your candidate of choice using the credentials above.
Login here: https://nacos-voting.netlify.app/

Best regards,
Idris David'''

    send_mail(
        subject,
        message,
        'noreply@mryamusa.tech',
        [user_email],
        fail_silently=False,
    )
