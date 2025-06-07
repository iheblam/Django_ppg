from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer

class CartView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart

class AddToCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        
        if quantity <= 0:
            return Response({"error": "Quantity must be greater than 0"}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
        except CartItem.DoesNotExist:
            cart_item = CartItem.objects.create(
                cart=cart,
                product_id=product_id,
                quantity=quantity
            )
        
        serializer = CartSerializer(cart)
        return Response(serializer.data)

class UpdateCartItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request, item_id):
        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
        
        quantity = int(request.data.get('quantity', 0))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        elif quantity == 0:
            cart_item.delete()
        
        cart = Cart.objects.get(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

class RemoveFromCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, item_id):
        try:
            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
            cart_item.delete()
        except CartItem.DoesNotExist:
            return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
        
        cart = Cart.objects.get(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)