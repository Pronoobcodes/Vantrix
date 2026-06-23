from django.urls import path
from . import views


urlpatterns = [
    path('create/', views.CreateReviewView.as_view(), name='create-review'),
    path('given/', views.ReviewsGivenView.as_view(), name='reviews-given'),
    path('received/', views.ReviewsReceivedView.as_view(), name='reviews-received'),
    path('detail/<int:pk>/', views.ReviewDetailView.as_view(), name='review-detail'),
    path('delete/<int:pk>/', views.ReviewDeleteView.as_view(), name='review-delete'),
    path('stats/<int:user_id>/', views.ReviewStatsView.as_view(), name='review-stats'),
]