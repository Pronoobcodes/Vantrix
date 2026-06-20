import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import Payment
from .serializers import PaymentSerializer
from .services import PaystackService
from orders.models import Order


class InitializePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        order_id = request.data.get('order_id')
        try:
            order = Order.objects.get(id=order_id, buyer=user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        reference = str(uuid.uuid4())
        callback_url = request.build_absolute_uri('/vantrix/payments/verify/')
        paystack_response = PaystackService.initialize_payment(
            email=user.email,
            amount=order.total_amount,
            reference=reference,
            callback_url=callback_url
        )

        if paystack_response and paystack_response.get('status'):
            payment_data = paystack_response['data']
            Payment.objects.create(
                user=user,
                order=order,
                gateway_reference=payment_data['reference'],
                amount=order.total_amount,
                currency='NGN',
                reference=reference
            )
            return Response({"authorization_url": payment_data['authorization_url']})
        
        return Response({"error": "Failed to initialize payment"}, status=400)
    

class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reference = request.query_params.get('reference')
        if not reference:
            return Response({"error": "Reference is required"}, status=400)

        payment = Payment.objects.filter(reference=reference, user=request.user).first()
        if not payment:
            return Response({"error": "Payment not found"}, status=404)

        paystack_response = PaystackService.verify_payment(reference)
        if paystack_response and paystack_response.get('status'):
            payment_data = paystack_response['data']
            payment.gateway_response = payment_data
            if payment_data['status'] == 'success':
                payment.status = 'COMPLETED'
                payment.order.status = 'paid'
                payment.order.save()
            else:
                payment.status = 'FAILED'
            payment.save()
            return Response({"message": "Payment verified", "payment_status": payment.status})
        
        return Response({"error": "Failed to verify payment"}, status=400)
    

class PaystackWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        payload = request.data
        reference = payload.get('data', {}).get('reference')
        if not reference:
            return Response({"error": "Reference is required"}, status=400)

        payment = Payment.objects.filter(reference=reference).first()
        if not payment:
            return Response({"error": "Payment not found"}, status=404)

        # Verify the payment with Paystack
        paystack_response = PaystackService.verify_payment(reference)
        if paystack_response and paystack_response.get('status'):
            payment_data = paystack_response['data']
            payment.gateway_response = payment_data
            if payment_data['status'] == 'success':
                payment.status = 'COMPLETED'
                payment.order.status = 'paid'
                payment.order.save()
            else:
                payment.status = 'FAILED'
            payment.save()

        return Response({"message": "Webhook processed successfully"})


class PaymentListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        payments = Payment.objects.filter(user=request.user)
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)