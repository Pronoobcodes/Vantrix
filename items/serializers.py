from rest_framework import serializers
from .models import Item, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']
        read_only_fields = ['id']


class ItemSerializer(serializers.ModelSerializer):
    category = serializers.CharField()
    owner = serializers.ReadOnlyField(source='owner.username')
    is_available = serializers.ReadOnlyField()
    image = serializers.ImageField(allow_empty_file=False, required=False)

    class Meta:
        model = Item
        fields = ['id', 'name', 'description', 'slug', 'price', 'image', 'category', 'owner', 'stock','is_available', 'created_at']
        read_only_fields = ['id', 'owner', 'created_at', 'slug']

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative")
        return value

    def validate_image(self, value):
        if value:
            if value.size > 5 * 1024 * 1024:  # 5MB limit
                raise serializers.ValidationError("Image size must be less than 5MB")
        return value    

    def create(self, validated_data):
        category_name = validated_data.pop('category')
        category, created = Category.objects.get_or_create(name=category_name.strip().title())

        item = Item.objects.create(
            category=category,
            **validated_data
        )

        return item
  


