from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Order, OrderItem
from .serializers import OrderSerializer
from cart.models import Cart

# Custom permission for admin users only
class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'ADMIN'


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class CreateOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)

        if not cart.items.exists():
            return Response({"error": "Your cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order_data = {
                'user': request.user,
                'full_name': request.data.get('full_name'),
                'email': request.data.get('email'),
                'phone_number': request.data.get('phone_number'),
                'address': request.data.get('address'),
                'city': request.data.get('city'),
                'state': request.data.get('state'),
                'zip_code': request.data.get('zip_code'),
                'payment_method': 'COD',
                'total': cart.get_total_price()
            }

            required_fields = ['full_name', 'email', 'phone_number', 'address', 'city', 'state', 'zip_code']
            for field in required_fields:
                if not order_data.get(field):
                    return Response({"error": f"{field} is required"}, status=status.HTTP_400_BAD_REQUEST)

            order = Order.objects.create(**order_data)

            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    price=cart_item.product.price,
                    quantity=cart_item.quantity
                )

            cart.items.all().delete()

            try:
                self.send_order_confirmation_email(order)
            except Exception as email_error:
                print(f"Email error: {email_error}")

            return Response({
                "order": OrderSerializer(order).data,
                "message": "Order created successfully"
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def send_order_confirmation_email(self, order):
        subject = f"Order Confirmation - Order #{order.id}"

        html_message = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #f8f9fa; padding: 15px; border-bottom: 3px solid #007bff; text-align: center; }}
                .content {{ padding: 20px 0; }}
                .footer {{ background-color: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; color: #6c757d; }}
                table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Thank You for Your Order!</h2>
                </div>
                <div class="content">
                    <p>Dear {order.full_name},</p>
                    <p>We are pleased to confirm that your order has been received and is being processed.</p>
                    
                    <h3>Order Details:</h3>
                    <p><strong>Order Number:</strong> #{order.id}</p>
                    <p><strong>Order Date:</strong> {order.created_at.strftime('%B %d, %Y')}</p>
                    <p><strong>Total Amount:</strong> ${order.total}</p>
                    <p><strong>Payment Method:</strong> Cash on Delivery</p>
                    
                    <h3>Shipping Address:</h3>
                    <p>{order.address}<br>
                    {order.city}, {order.state} {order.zip_code}</p>
                    
                    <h3>Order Items:</h3>
                    <table>
                        <tr>
                            <th>Product</th>
                            <th>Quantity</th>
                            <th>Price</th>
                        </tr>
                        {''.join(f"<tr><td>{item.product.name}</td><td>{item.quantity}</td><td>${item.price}</td></tr>" for item in order.items.all())}
                    </table>
                    
                    <p>We will notify you when your order has been shipped.</p>
                    <p>If you have any questions about your order, please contact our customer service.</p>
                    <p>Thank you for shopping with us!</p>
                </div>
                <div class="footer">
                    <p>&copy; {timezone.now().year} Your Company Name. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        plain_message = f"""
        Dear {order.full_name},

        Thank you for your order! Your order #{order.id} has been received and is being processed.

        Order Details:
        - Order ID: {order.id}
        - Total: ${order.total}
        - Payment Method: Cash on Delivery
        - Shipping Address: {order.address}, {order.city}, {order.state}, {order.zip_code}

        We will notify you when your order has been shipped.

        Thank you for shopping with us!
        """

        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [order.email],
            html_message=html_message,
            fail_silently=False,
        )


# Admin Views

class AdminOrderListView(generics.ListAPIView):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(order_status=status_filter)
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "orders": serializer.data,
            "count": queryset.count()
        })


class AdminOrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if 'order_status' in request.data:
            instance.order_status = request.data.get('order_status')
            instance.save()

            if request.data.get('send_notification', False):
                self.send_status_update_email(instance)

            return Response(OrderSerializer(instance).data)
        return Response({"error": "Only order status can be updated"}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.order_status in ['SHIPPED', 'DELIVERED']:
            return Response(
                {"error": f"Cannot delete orders with status '{instance.order_status}'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        order_id = instance.id
        instance.delete()
        return Response(
            {"message": f"Order #{order_id} has been deleted successfully"},
            status=status.HTTP_200_OK
        )

    def send_status_update_email(self, order):
        subject = f"Order Status Update - Order #{order.id}"
        message = f"""
        Dear {order.full_name},

        Your order #{order.id} status has been updated to: {order.get_order_status_display()}

        Thank you for shopping with us!
        """
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [order.email],
            fail_silently=False,
        )
