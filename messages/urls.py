from django.urls import path
from . import views

urlpatterns = [
    path('conversations/', views.ConversationListCreateView.as_view(), name='conversation-list-create'),
    path('conversations/<int:pk>/', views.ConversationDetailView.as_view(), name='conversation-detail'),
    path('conversations/<int:conversation_id>/send_message/', views.SendMessageView.as_view(), name='send-message'),
    path('conversations/<int:conversation_id>/add_message/', views.AddMessageView.as_view(), name='add-message'),
    path('conversations/<int:conversation_id>/send_offer/', views.SendOfferView.as_view(), name='send-offer'),
    path('messages/<int:message_id>/accept_offer/', views.AcceptOfferView.as_view(), name='accept-offer'),
    path('messages/<int:message_id>/reject_offer/', views.RejectOfferView.as_view(), name='reject-offer'),
    path('messages/<int:message_id>/delete/', views.DeleteMessageView.as_view(), name='delete-message'),
    path('messages/<int:message_id>/update/', views.UpdateMessageView.as_view(), name='update-message'),
    path('conversations/<int:conversation_id>/unread_count/', views.UnreadMessagesCountView.as_view(), name='unread-messages-count'),
]