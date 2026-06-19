from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Order, OrderItem, Escrow
from items.models import Item

User = get_user_model()


class OrderItemSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = OrderItem
        fields = ['id', 'item', 'item_title', 'item_price', 'quantity']


class EscrowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Escrow
        fields = ['id', 'amount', 'status', 'held_at', 'released_at']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    escrow = EscrowSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'buyer', 'seller', 'status', 'total_amount', 'shipping_address', 'tracking_number', 'logistics_partner', 'buyer_confirmed', 'created_at', 'updated_at', 'items', 'escrow']
        read_only_fields = ['id', 'buyer', 'seller', 'status', 'total_amount', 'created_at', 'updated_at']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        return order


class CheckoutItemSerializer(serializers.Serializer):
    item_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)

    def validate_item_id(self, value):
        try:
            item = Item.objects.get(id=value)
        except Item.DoesNotExist:
            raise serializers.ValidationError("Item does not exist")

        if not item.is_available:
            raise serializers.ValidationError("Item is not available for purchase")

        return value
    

class CheckoutSerializer(serializers.Serializer):
    seller_id = serializers.UUIDField()
    shipping_address = serializers.JSONField()
    items = CheckoutItemSerializer(many=True)

    def validate_seller_id(self, value):
        try:
            User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Seller does not exist")
        return value

    def create(self, validated_data):
        buyer = self.context['request'].user
        items_data = validated_data.pop('items')
        total = Decimal('0.00')
        seller_id = validated_data['seller_id']

        order = Order.objects.create(
            buyer=buyer,
            seller_id=seller_id,
            shipping_address=validated_data['shipping_address'],
            total_amount=total
        )

        for item_data in items_data:
            item = Item.objects.get(id=item_data['item_id'])
            quantity = item_data['quantity']
            total += item.price * quantity

            OrderItem.objects.create(
                order=order,
                item=item,
                item_title=item.name,
                item_price=item.price,
                quantity=quantity
            )

        order.total_amount = total
        order.save()
        return order
    