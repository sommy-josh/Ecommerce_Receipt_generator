from rest_framework import serializers
from .models import Order, OrderItem
from django.contrib.auth.models import User


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ["product_name", "quantity", "unit_price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ["order_id", "payment_method", "is_paid", "created_at", "items"]
        read_only_fields = ["order_id", "is_paid", "created_at"]

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        user = self.context["request"].user

        order = Order.objects.create(
            user=user,
            total_amount=0,
            **validated_data
        )

        total = 0

        for item_data in items_data:
            item = OrderItem.objects.create(order=order, **item_data)
            total += item.get_total()

        order.total_amount = total
        order.save()

        return order

    def update(self, instance, validated_data):
        # Prevent updating paid orders
        if instance.is_paid:
            raise serializers.ValidationError(
                "Paid orders cannot be updated."
            )

        items_data = validated_data.pop("items", None)

        # Update payment method if provided
        instance.payment_method = validated_data.get(
            "payment_method",
            instance.payment_method
        )
        instance.save()

        # If items are provided, replace them
        if items_data is not None:
            # Delete old items
            instance.items.all().delete()

            total = 0

            for item_data in items_data:
                item = OrderItem.objects.create(
                    order=instance,
                    **item_data
                )
                total += item.get_total()

            instance.total_amount = total
            instance.save()

        return instance

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user