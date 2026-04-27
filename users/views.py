from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import CreateAPIView, GenericAPIView,RetrieveUpdateAPIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    CustomUserSerializer, UserRegistrationSerializer, UserLoginSerializer, ProfileSerializer
)
from .models import Profile


class UserRegistrationView(CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    

class UserLoginView(GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)

            return Response({
                'user': CustomUserSerializer(user).data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            })

        return Response(serializer.errors, status=400)
    

class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserProfileView(RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile
    