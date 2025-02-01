import random
import string

def generate_password():
    """Generate a random 12-character password"""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(12))

def send_credentials_email(user_email, username, password):
    from django.core.mail import send_mail
    
    subject = f'Hi {username}, here\'s your Election Username and Password'
    message = f'''Hello!

Thank you for registering! Your voting account has been created successfully.

Username: {username}
Password: {password}

Please login to vote for your candidate of choice using the credentials above.

Best regards,
Idris David'''

    send_mail(
        subject,
        message,
        'noreply@mryamusa.tech',
        [user_email],
        fail_silently=False,
    )
