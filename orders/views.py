from django.shortcuts import render,get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .models import Order,OrderItem,Receipt
from .utils import generate_receipt_pdf
from .serializers import OrderSerializer,RegisterSerializer,MessageSerializer,ErrorSerializer
import cloudinary
import cloudinary.uploader

@extend_schema(
    tags=["Payments"],
    responses={200: MessageSerializer}
)
@api_view(['POST'])
def confirm_payment(request, order_id):

    order = get_object_or_404(Order, order_id=order_id)

    if order.is_paid:
        return Response(
            {"message": "Order already paid."},
            status=status.HTTP_400_BAD_REQUEST
        )

    order.is_paid = True
    order.save()

    #  Create receipt safely
    receipt, created = Receipt.objects.get_or_create(order=order)

    if created:
        # Generate PDF
        pdf_path = generate_receipt_pdf(order)

        # Upload to Cloudinary
        upload_result = cloudinary.uploader.upload(
            pdf_path,
            resource_type="raw"
        )

        receipt.pdf_url = upload_result["secure_url"]
        receipt.save()

    return Response({
        "message": "Payment confirmed. Receipt generated.",
        "pdf_url": receipt.pdf_url
    })




@extend_schema(
    request=OrderSerializer,
    responses={
        201: OrderSerializer,
        400: OpenApiTypes.OBJECT
    }
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_order(request):
    serializer = OrderSerializer(data=request.data, context={"request": request})

    if serializer.is_valid():
        order = serializer.save()
        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@extend_schema(
    responses={200: OrderSerializer(many=True)}
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="order_id",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description="Unique order ID"
        )
    ],
    responses={200: OrderSerializer}
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def retrieve_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    serializer = OrderSerializer(order)
    return Response(serializer.data)


@extend_schema(
    request=OrderSerializer,
    parameters=[
        OpenApiParameter(
            name="order_id",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description="Unique order ID"
        )
    ],
    responses={
        200: OrderSerializer,
        400: ErrorSerializer
    }
)
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


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="order_id",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description="Unique order ID"
        )
    ],
    responses={
        204: MessageSerializer,
        400: ErrorSerializer
    }
)
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


@extend_schema(
    request=RegisterSerializer,
    responses={
        201: MessageSerializer,
        400: OpenApiTypes.OBJECT
    }
)
@api_view(["POST"])
def register_user(request):
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "User registered successfully"},
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
