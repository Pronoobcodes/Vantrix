from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Profile


User = get_user_model()


class UserAccountSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    email = serializers.EmailField(required=False)
    username = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['email', 'username', 'password']

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance    


class ProfileSerializer(serializers.ModelSerializer): 
    user = UserAccountSerializer()

    class Meta:
        model = Profile
        fields = ['user','bio', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class CustomUserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username',
            'phone_number', 'is_active',
            'date_joined', 'profile'
        ]
        read_only_fields = ['id', 'is_active', 'date_joined']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value.lower()

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            username=data.get('email'),
            password=data.get('password')
        )

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled")

        data['user'] = user
        return data
    

