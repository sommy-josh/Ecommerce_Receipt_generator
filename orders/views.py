from django.shortcuts import render,get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from .models import Order,OrderItem
from .serializers import OrderSerializer

@api_view(['POST'])
def confirm_payment(request, order_id):
    order=Order.objects.get(order_id=order_id)
    order.is_paid=True
    order.save()
    return Response({"message": "Payment confirmed. Receipt generated."})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_order(request):
    serializer = OrderSerializer(data=request.data, context={"request": request})

    if serializer.is_valid():
        order = serializer.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def retrieve_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    serializer = OrderSerializer(order)
    return Response(serializer.data)

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)

    if order.is_paid:
        return Response(
            {"error": "Paid orders cannot be updated."},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = OrderSerializer(order, data=request.data, context={"request": request})
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)

    if order.is_paid:
        return Response(
            {"error": "Paid orders cannot be deleted."},
            status=status.HTTP_400_BAD_REQUEST
        )

    order.delete()
    return Response(
        {"message": "Order deleted successfully."},
        status=status.HTTP_204_NO_CONTENT
    )