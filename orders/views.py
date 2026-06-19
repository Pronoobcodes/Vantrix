from django.utils import timezone

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Order, Escrow
from .serializers import OrderSerializer, CheckoutSerializer


class CheckoutView(generics.CreateAPIView):
    serializer_class = CheckoutSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        output_serializer = OrderSerializer(order)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class BuyerOrdersView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Order.objects.filter(buyer=self.request.user)
            .select_related('seller', 'escrow')
            .prefetch_related('items')
            .order_by('-created_at')
        )


class SellerOrdersView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Order.objects.filter(seller=self.request.user)
            .select_related('buyer', 'escrow')
            .prefetch_related('items')
            .order_by('-created_at')
        )
    

class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        return Order.objects.all()
    

class MarkOrderPaidView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        order = Order.objects.get(id=order_id)

        if order.status != "pending":
            return Response({"detail": "Order already processed"},status=status.HTTP_400_BAD_REQUEST)

        order.status = "paid"
        order.save()

        Escrow.objects.create(
            order=order,
            amount=order.total_amount,
        )

        return Response({"message": "Payment confirmed"})   


class ShipOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        order = Order.objects.get(id=order_id)

        if request.user != order.seller:
            return Response(
                {"detail": "Not allowed"},
                status=status.HTTP_403_FORBIDDEN,
            )

        tracking_number = request.data.get("tracking_number")
        logistics_partner = request.data.get("logistics_partner")

        order.tracking_number = tracking_number
        order.logistics_partner = logistics_partner
        order.status = "shipped"
        order.save()

        return Response({"message": "Order shipped"})
    

class ConfirmDeliveryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        order = Order.objects.get(id=order_id)

        if request.user != order.buyer:
            return Response(
                {"detail": "Not allowed"},
                status=status.HTTP_403_FORBIDDEN,
            )

        order.buyer_confirmed = True
        order.status = "delivered"
        order.save()

        escrow = order.escrow

        escrow.status = "released"
        escrow.released_at = timezone.now()
        escrow.save()

        return Response(
            {"message": "Delivery confirmed. Escrow released."}
        )
    

class OpenDisputeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        order = Order.objects.get(id=order_id)

        if request.user != order.buyer:
            return Response(
                {"detail": "Not allowed"},
                status=status.HTTP_403_FORBIDDEN,
            )

        order.status = "disputed"
        order.save()

        return Response(
            {"message": "Dispute opened"}
        )
    

class RefundOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        order = Order.objects.get(id=order_id)

        order.status = "refunded"
        order.save()

        escrow = order.escrow
        escrow.status = "refunded"
        escrow.released_at = timezone.now()
        escrow.save()

        return Response(
            {"message": "Order refunded"}
        )