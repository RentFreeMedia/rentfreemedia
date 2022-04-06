from django.urls import include, path, re_path
from django.views.decorators.csrf import csrf_exempt
from djstripe.views import ProcessWebhookView
from payments.views import (
	subscribe_switch_view,
    subscribe_new,
    subscribe_update,
    subscribe_checkout_session,
    subscribe_price_change,
    subscribe_canceled,
    subscribe_card_change_canceled,
    subscribe_card_change_session,
    subscribe_card_change_complete,
    subscribe_complete,
    subscribe_stripe_config,
    reset_user
)

urlpatterns = [
	path('subscribe-stripe-config/', subscribe_stripe_config, name='subscribe_stripe_config'),
    path('subscribe/', subscribe_switch_view(subscribe_new, subscribe_update), name='subscribe'),
    path('subscribe-checkout-session/', subscribe_checkout_session, name='subscribe_checkout_session'),
    path('subscribe-price-change/', subscribe_price_change, name='subscribe_price_change'),
    path('subscribe-card-change-complete/<session_id>/', subscribe_card_change_complete, name='subscribe_card_change_complete'),
    path('subscribe-complete/<session_id>/', subscribe_complete, name='subscribe_complete'),
    path('subscribe-canceled/', subscribe_canceled, name='subscribe_canceled'),
    path('subscribe-card-change-canceled/', subscribe_card_change_canceled, name='subscribe_card_change_canceled'),
    path('subscribe-card-change-session/', subscribe_card_change_session, name='subscribe_card_change_session'),
    path('subscribe-events/', csrf_exempt(ProcessWebhookView.as_view()), name='webhook'),
    path('reset-user/<uidb64>/', reset_user, name='reset_user')
]