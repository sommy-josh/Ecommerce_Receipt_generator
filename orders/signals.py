from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, Receipt
from .utils import generate_receipt_pdf
from .email_utils import send_receipt_email



@receiver(post_save, sender=Order)
def generate_receipt_on_payment(sender, instance, created, **kwargs):

    # Only run when payment is confirmed
    if not instance.is_paid:
        return

    # Prevent duplicate receipts
    if Receipt.objects.filter(order=instance).exists():
        return  # Receipt already exists

    # Create receipt
    receipt = Receipt.objects.create(order=instance)

    # Generate PDF
    pdf_url = generate_receipt_pdf(instance)

    # Save PDF URL
    receipt.pdf = pdf_url
    receipt.save()

    # Send email
    send_receipt_email(instance.user.email, pdf_url, instance)
