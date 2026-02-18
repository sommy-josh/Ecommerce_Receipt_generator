import os
import cloudinary.uploader
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime


def generate_receipt_pdf(order):
    """
    Generates a receipt PDF, uploads to Cloudinary,
    and returns the Cloudinary secure URL.
    """

    # Ensure receipts directory exists
    receipts_dir = os.path.join(settings.MEDIA_ROOT, "receipts")
    os.makedirs(receipts_dir, exist_ok=True)

    filename = f"order_{order.id}_receipt.pdf"
    file_path = os.path.join(receipts_dir, filename)

    # Generate PDF
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 50, "Payment Receipt")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 100, f"Order ID: {order.id}")
    c.drawString(50, height - 130, f"Customer: {order.user.email}")
    c.drawString(50, height - 160, f"Amount Paid: ₦{order.total_amount}")
    c.drawString(50, height - 190, "Payment Status: PAID")
    c.drawString(
        50,
        height - 220,
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    c.showPage()
    c.save()

    #  Upload to Cloudinary (IMPORTANT: resource_type="raw")
    upload_result = cloudinary.uploader.upload(
        file_path,
        resource_type="raw"
    )

    # Optional: delete local file after upload
    os.remove(file_path)

    # Return Cloudinary URL
    return upload_result.get("secure_url")
