from django.core.mail import send_mail
from django.conf import settings

def send_receipt_email(user, receipt_url, order):
    subject = f"Your Receipt for Order #{order.id}"
    message =f"""
Hi {user.first_name},

Thank you for your payment. You can download your receipt here:

{receipt_url}

Best regards,
Chisom Stores
""" 
    print(message)
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
