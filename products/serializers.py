# products/serializers.py - Updated with image handling
from rest_framework import serializers
from .models import Category, Product

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    image = serializers.ImageField(required=False, allow_null=True)
    
    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'price', 'image', 'category', 
                  'category_name', 'product_type', 'is_active', 'created_at')
    
    def create(self, validated_data):
        return Product.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        # Handle image update
        image = validated_data.get('image', None)
        if image:
            # Delete old image if it exists
            if instance.image:
                instance.image.delete(save=False)
            instance.image = image
        
        # Update other fields
        for attr, value in validated_data.items():
            if attr != 'image':
                setattr(instance, attr, value)
        
        instance.save()
        return instance


class CategorySerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)
    products_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'image', 'is_active', 'created_at', 'updated_at', 'products_count')
    
    def get_products_count(self, obj):
        return obj.products.filter(is_active=True).count()
    
    def create(self, validated_data):
        return Category.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        # Handle image update
        image = validated_data.get('image', None)
        if image:
            # Delete old image if it exists
            if instance.image:
                instance.image.delete(save=False)
            instance.image = image
        
        # Update other fields
        for attr, value in validated_data.items():
            if attr != 'image':
                setattr(instance, attr, value)
        
        instance.save()
        return instance