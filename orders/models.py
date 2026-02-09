from django.db import models
from django.contrib.auth.models import User
import uuid

class Order(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    order_id=models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    total_amount=models.DecimalField(max_digits=10, decimal_places=2)
    payment_method=models.CharField(max_length=50)
    is_paid=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.order_id)

class OrderItem(models.Model):
    order=models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product_name= models.CharField(max_length=50)
    quantity=models.PositiveIntegerField()
    unit_price=models.DecimalField(max_digits=10, decimal_places=2)

    def get_total(self):
        return self.quantity * self.unit_price

    def __str__(self):
        return self.product_name
    
class Receipt(models.Model):
    receipt_id=models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    order=models.OneToOneField(Order, on_delete=models.CASCADE)
    pdf_url=models.URLField(blank=True, null=True)
    created_at=models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return str(self.receipt_id)

