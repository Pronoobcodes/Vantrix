import django_filters.rest_framework
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.filters import SearchFilter, OrderingFilter 
from rest_framework.pagination import PageNumberPagination

from .models import Item, Category
from .serializers import ItemSerializer, CategorySerializer
from .filters import ItemFilter




class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or request.user.is_staff


class ItemViewSet(ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    pagination_class = PageNumberPagination

    filter_backends = [django_filters.rest_framework.DjangoFilterBackend, SearchFilter, OrderingFilter, ItemFilter]

    filterset_fields = ['category', 'price', 'stock']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]

        if self.action == 'create':
            return [IsAuthenticated()]

        return [IsAuthenticated(), IsOwnerOrAdmin()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CategoryListView(ListAPIView):
    queryset = Category.objects.all() 
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
