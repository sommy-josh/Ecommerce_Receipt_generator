import os
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime


def generate_receipt_pdf(order):
    """
    Generates a receipt PDF locally and returns the file path
    """

    # Ensure receipts directory exists
    receipts_dir = os.path.join(settings.MEDIA_ROOT, "receipts")
    os.makedirs(receipts_dir, exist_ok=True)

    file_path = os.path.join(
        receipts_dir,
        f"order_{order.id}_receipt.pdf"
    )

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    # Title
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 50, "Payment Receipt")

    # Body
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 100, f"Order ID: {order.id}")
    c.drawString(50, height - 130, f"Customer: {order.user.email}")
    c.drawString(50, height - 160, f"Amount Paid: ₦{order.total_amount}")
    c.drawString(50, height - 190, f"Payment Status: PAID")
    c.drawString(
        50,
        height - 220,
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    c.showPage()
    c.save()

    return file_path  # ⚠️ LOCAL FILE PATH ONLY
