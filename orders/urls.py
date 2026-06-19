from django.urls import path

from .views import (
    CheckoutView,
    BuyerOrdersView,
    SellerOrdersView,
    OrderDetailView,
    MarkOrderPaidView,
    ShipOrderView,
    ConfirmDeliveryView,
    OpenDisputeView,
    RefundOrderView,
)

urlpatterns = [
    path(
        "checkout/",
        CheckoutView.as_view(),
        name="checkout",
    ),

    path(
        "buyer/",
        BuyerOrdersView.as_view(),
        name="buyer-orders",
    ),

    path(
        "seller/",
        SellerOrdersView.as_view(),
        name="seller-orders",
    ),

    path(
        "<uuid:id>/",
        OrderDetailView.as_view(),
        name="order-detail",
    ),

    path(
        "<uuid:order_id>/paid/",
        MarkOrderPaidView.as_view(),
        name="mark-paid",
    ),

    path(
        "<uuid:order_id>/ship/",
        ShipOrderView.as_view(),
        name="ship-order",
    ),

    path(
        "<uuid:order_id>/confirm-delivery/",
        ConfirmDeliveryView.as_view(),
        name="confirm-delivery",
    ),

    path(
        "<uuid:order_id>/dispute/",
        OpenDisputeView.as_view(),
        name="open-dispute",
    ),

    path(
        "<uuid:order_id>/refund/",
        RefundOrderView.as_view(),
        name="refund-order",
    ),
]