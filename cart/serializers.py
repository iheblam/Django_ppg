from rest_framework import serializers
from .models import Cart, CartItem
from products.serializers import ProductSerializer

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    subtotal = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = ('id', 'cart', 'product', 'product_id', 'quantity', 'subtotal')
        read_only_fields = ('cart',)
    
    def get_subtotal(self, obj):
        return obj.get_subtotal()

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ('id', 'items', 'total', 'created_at', 'updated_at')
    
    def get_total(self, obj):
        return obj.get_total_price()
