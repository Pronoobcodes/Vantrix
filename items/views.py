import django_filters.rest_framework
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter 
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Item, Category
from .serializers import ItemSerializer, CategorySerializer
from .filters import ItemFilter
from core.permissions import IsOwnerOrAdmin


class ItemViewSet(ModelViewSet):
    queryset = Item.objects.select_related('category', 'owner').all()
    serializer_class = ItemSerializer
    pagination_class = PageNumberPagination
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ItemFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']
    parser_classes = (MultiPartParser, FormParser)

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]

        if self.action == 'create':
            return [IsAuthenticated()]

        return [IsAuthenticated(), IsOwnerOrAdmin()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        items = Item.objects.filter(category_id=pk)

        page = self.paginate_queryset(items)
        if page is not None:
            serializer = ItemSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ItemSerializer(items, many=True)
        return Response(serializer.data)
