from django.contrib.auth import get_user_model

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Review
from .serializers import ReviewSerializer, CreateReviewSerializer
from .services import get_review_stats


user = get_user_model()

class CreateReviewView(generics.CreateAPIView):
    serializer_class = CreateReviewSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)


class ReviewsGivenView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(reviewer=self.request.user)
    

class ReviewsReceivedView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(reviewed_user=self.request.user)
    

class ReviewDetailView(generics.RetrieveAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(reviewed_user=self.request.user) | Review.objects.filter(reviewer=self.request.user)
    

class ReviewDeleteView(generics.DestroyAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(reviewer=self.request.user)
    

class ReviewStatsView(APIView):
    
    def get(self, request, user_id):
        try:
            user = user.objects.get(id=user_id)
        except user.DoesNotExist:
            return Response({"error": "User not found."}, status=404)

        stats = get_review_stats(user)
        return Response(stats)
    

