import resend
from django.conf import settings

resend.api_key = settings.RESEND_API_KEY

def send_receipt_email(user_email, receipt_url, order):
    """
    Sends receipt email with a link to download PDF
    """
    response = resend.Emails.send({
        "from": settings.DEFAULT_FROM_EMAIL, 
        "to": [user_email],                   
        "subject": f"Your Receipt for Order #{order.id}",
        "html": f"""
            <h2>Payment Successful 🎉</h2>
            <p>Hi {order.user.first_name} {order.user.last_name},</p>
            <p>Your payment has been confirmed.</p>
            <p><strong>Order ID:</strong> {order.id}</p>
            <p><strong>Amount:</strong> ₦{order.total_amount}</p>
            <br>
            <a href="{receipt_url}" target="_blank">
                Download Your Receipt
            </a>
            <br><br>
            <p>Thank you for your purchase.</p>
        """
    })
    return response
