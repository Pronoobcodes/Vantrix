from rest_framework import serializers
from .models import Review

from orders.models import Order


class ReviewSerializer(serializers.ModelSerializer):
    reviewer_username = serializers.CharField(source='reviewer.username', read_only=True)
    reviewed_user_username = serializers.CharField(source='reviewed_user.username', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'reviewer', 'reviewer_username', 'reviewed_user', 'reviewed_user_username', 'item', 'order', 'role', 'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'reviewer', 'reviewed_user', 'order', 'item']


class CreateReviewSerializer(serializers.ModelSerializer):
    order_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Review
        fields = ['order_id', 'role', 'rating', 'comment']

    def create(self, validated_data):
        user = self.context['request'].user
        order = Order.objects.get(id=validated_data['order_id'])

        if order.status != 'delivered':
            raise serializers.ValidationError("You can only review after the order is delivered.")
        
        if user == order.buyer:
            reviewed_user = order.seller
            role = 'buyer'

        elif user == order.seller:
            reviewed_user = order.buyer
            role = 'seller'

        else:
            raise serializers.ValidationError("You are not a participant in this order.")

        review = Review.objects.create(
            reviewer=user,
            reviewed_user=reviewed_user,
            item=order.item,
            order=order,
            role=role,
            rating=validated_data['rating'],
            comment=validated_data['comment']
        )
        return review