from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView

from .models import Item, Category
from .serializers import ItemSerializer, CategorySerializer


class ItemCreateListInfoRetrieveUpdateDestroyViewSet(ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CategoryListView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
