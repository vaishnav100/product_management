from rest_framework import serializers
from user_management.models import User, Token
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255, required=True)
    description = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    updated_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be a positive number.")
        return value

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("Name must be at least 3 characters long.")
        if Product.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("Product with this name already exists.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        return Product.objects.create(
            name=validated_data['name'].strip(),
            description=validated_data.get('description', '').strip(),
            price=validated_data['price'],
            created_by=user,
            updated_by=user
        )

    def update(self, instance, validated_data):
        user = self.context['request'].user
        if not (
            (instance.created_by == user and getattr(user, 'admin_approve', False)) or
            user.is_superuser or
            user.is_staff
        ):
            raise serializers.ValidationError("You do not have permission to update this product.")

        if 'name' in validated_data:
            name = validated_data['name'].strip()
            if Product.objects.filter(name__iexact=name).exclude(id=instance.id).exists():
                raise serializers.ValidationError("Product with this name already exists.")
            instance.name = name

        if 'description' in validated_data:
            instance.description = validated_data['description'].strip()

        if 'price' in validated_data:
            instance.price = validated_data['price']

        instance.updated_by = user
        instance.save()
        return instance
