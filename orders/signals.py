import os

from django.db.models.signals import post_save
from django.dispatch import receiver

import cloudinary.uploader

from .models import Order, Receipt
from .utils import generate_receipt_pdf
from .email_utils import send_receipt_email


@receiver(post_save, sender=Order)
def generate_receipt_on_payment(sender, instance, created, **kwargs):
    # Run only when payment is confirmed
    if not instance.is_paid:
        return

    # Prevent duplicate receipts
    if Receipt.objects.filter(order=instance).exists():
        return

    # Create receipt record
    receipt = Receipt.objects.create(order=instance)

    # Generate PDF locally
    pdf_path = generate_receipt_pdf(instance)

    if not pdf_path or not os.path.exists(pdf_path):
        return

    # Upload to Cloudinary (RAW)
    upload_result = cloudinary.uploader.upload(
        pdf_path,
        resource_type="raw",
        folder="receipts"
    )

    # Save Cloudinary URL
    receipt.pdf_url = upload_result["secure_url"]
    receipt.save()

    # Send email with download link
    send_receipt_email(
        user=instance.user,
        receipt_url=f"{receipt.pdf_url}?dl=1",
        order=instance
    )

    # Delete local PDF
    try:
        os.remove(pdf_path)
    except OSError:
        pass
