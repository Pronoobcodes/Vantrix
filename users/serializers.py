from rest_framework import serializers
from .models import CustomUser,EmailVerification


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'
        read_only_fields = ('id', 'is_active', 'is_staff', 'email_verified', 'phone_verified', 'date_joined', 'last_login')


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser.profile.related_model
        fields = '__all__'
        read_only_fields = ('user', 'karma_score', 'created_at', 'updated_at', 'total_sales', 'total_purchases')


class EmailVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailVerification
        fields = '__all__'
        read_only_fields = ('user', 'verification_type', 'token', 'is_verified', 'verified_at', 'created_at')


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'password')

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    



