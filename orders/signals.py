import os
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Order, Receipt
from .utils import generate_receipt_pdf
from .email_utils import send_receipt_email


@receiver(post_save, sender=Order)
def generate_receipt_on_payment(sender, instance, created, **kwargs):
    """
    Generates a PDF receipt and emails the user when order is paid.
    """
    if not instance.is_paid:
        return

    # Prevent duplicate receipts
    if Receipt.objects.filter(order=instance).exists():
        return

    # Generate PDF and get URL
    pdf_url = generate_receipt_pdf(instance)
    if not pdf_url:
        return  # optionally log failure

    # Create receipt record
    receipt = Receipt.objects.create(order=instance, pdf_url=pdf_url)

    # Send receipt email
    send_receipt_email(
        user_email=instance.user.email,
        receipt_url=f"{receipt.pdf_url}?dl=1",
        order=instance
    )
