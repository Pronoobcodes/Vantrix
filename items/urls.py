from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('products', views.ItemViewSet, basename='products')
router.register('categories', views.CategoryViewSet, basename='categories')

urlpatterns = router.urls


