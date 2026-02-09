from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Order

@api_view(['POST'])
def confirm_payment(request, order_id):
    order=Order.objects.get(order_id=order_id)
    order.is_paid=True
    order.save()
    return Response({"message": "Payment confirmed. Receipt generated."})
