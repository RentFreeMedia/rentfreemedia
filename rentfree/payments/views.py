import json
from post_office import mail
import stripe
import uuid
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.db.models.query_utils import Q
from django.forms.models import model_to_dict
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template import Context, loader
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from djstripe.models import Product, Customer, Subscription, Price, PaymentMethod
from users.tokens import subscribe_token, cardchange_token, premium_token
from website.models.pages import PodcastContentPage, ArticleContentPage 
from website.models.rules import TierEqualOrGreater, TierEqual
from website.wagtail_hooks import DownloadAdmin

UserModel = get_user_model()

@csrf_exempt
@login_required
def subscribe_stripe_config(request):
    if request.method == 'GET':
        if settings.STRIPE_LIVE_MODE == 'True':
            stripe_config = {'publicKey': settings.STRIPE_LIVE_PUBLIC_KEY}
        else:
            stripe_config = {'publicKey': settings.STRIPE_TEST_PUBLIC_KEY}
        return JsonResponse(stripe_config, safe=False)


def subscribe_switch_view(freeuser_view, paiduser_view):

    @login_required
    def inner_view(request, *args, **kwargs):
        user_level = request.user.is_paysubscribed
        if user_level == 0:
            return freeuser_view(request, *args, **kwargs)
        else:
            return paiduser_view(request, *args, **kwargs)

    return inner_view


@login_required
@require_POST
def subscribe_card_change_session(request):

    if settings.STRIPE_LIVE_MODE == 'True':
        stripe.api_key = settings.STRIPE_LIVE_SECRET_KEY
    else:
        stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

    data = json.loads(request.body)
    token = cardchange_token.make_token(request.user)
    paymethod_obj = PaymentMethod.objects.get(pk=request.user.stripe_paymentmethod.djstripe_id)
    customer_obj = Customer.objects.get(pk=request.user.stripe_customer.djstripe_id)
    subscription_obj = Subscription.objects.get(pk=request.user.stripe_subscription.djstripe_id)

    card_change_session = stripe.checkout.Session.create(
        payment_method_types = ['card'],
        mode = 'setup',
        customer = customer_obj.id,
        metadata = {'token': token},
        setup_intent_data = {
            'metadata': {
                'subscription_id': subscription_obj.id,
            },
        },
        success_url = data['domain'] + '/subscribe-card-change-complete/{CHECKOUT_SESSION_ID}/',
        cancel_url = data['domain'] + '/subscribe-card-change-canceled/',
    )
    try:
        return JsonResponse({'sessionId': card_change_session['id']})
    except Exception as e:
        return JsonResponse({'error': e})


@login_required
@require_POST
def subscribe_checkout_session(request):

    if settings.STRIPE_LIVE_MODE == 'True':
        stripe.api_key = settings.STRIPE_LIVE_SECRET_KEY
    else:
        stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

    data = json.loads(request.body)
    token = subscribe_token.make_token(request.user)
    product_obj = Product.objects.get(metadata={'tier': data['product_tier']})
    price_obj = Price.objects.get(product_id=product_obj.id)

    checkout_session = stripe.checkout.Session.create(
        success_url = data['domain'] + '/subscribe-complete/{CHECKOUT_SESSION_ID}/',
        cancel_url = data['domain'] + '/subscribe-canceled/',
        payment_method_types = ['card'],
        allow_promotion_codes=True,
        mode = 'subscription',
        customer_email = request.user.email,
        metadata = {'token': token},
        line_items = [
            {
                'price': price_obj.id,
                'quantity': 1,
            }
        ]
    )
    try:
        return JsonResponse({'sessionId': checkout_session['id']})
    except Exception as e:
        return JsonResponse({'error': e})


@transaction.atomic
@login_required
@require_POST
def subscribe_price_change(request, *args, **kwargs):

    if settings.STRIPE_LIVE_MODE == 'True':
        stripe.api_key = settings.STRIPE_LIVE_SECRET_KEY
    else:
        stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

    new_tier = request.POST['prod_tier']

    if new_tier != '0' and request.user.is_paysubscribed > 0:
        try:
            user = request.user
            product_obj = Product.objects.get(metadata={'tier': new_tier})
            price_obj = Price.objects.get(product_id=product_obj.id)
            subscription_obj = Subscription.objects.get(djstripe_id=user.stripe_subscription_id)
            subscription = stripe.Subscription.retrieve(subscription_obj.id)

        except Exception:
            user = None

        if user and subscription.cancel_at_period_end == True:
            change_subscription = stripe.Subscription.modify(
                subscription.id,
                cancel_at_period_end=False,
                proration_behavior='create_prorations',
                items=[
                    {
                        'id': subscription['items']['data'][0].id,
                        'price': price_obj.id,
                    }
                ]
            )
            djstripe_subscription = Subscription.sync_from_stripe_data(change_subscription)
            user.stripe_subscription = djstripe_subscription
            user.is_paysubscribed = new_tier
            user.paysubscribe_changed = timezone.now()
            user.save()

            user_context = model_to_dict(user, exclude=['groups', 'password', 'user_permissions'])
            request_context = { 'request': request }
            template = loader.get_template('payments/email/subscribe_change.txt')
            context = {**user_context, **request_context}
            html_message = template.render(context)
            mail.send(
                user.email,
                settings.EMAIL_ADDR,
                subject='Subscription change confirmation for ' + request.get_host(),
                html_message=html_message
            )

            return render(request, 'payments/subscribe_complete.html')
        elif user and subscription.cancel_at_period_end == False:
            """Optionally, you could add flood control here by checking 
            paysubscribe_changed versus timezone.now() for users who
            are not presently set to cancel, to prevent flooding the
            Stripe API with subscription changes. By default this
            method is identical to the subscription change method for
            users who *are* set to cancel at billing cycle end."""
            change_subscription = stripe.Subscription.modify(
                subscription.id,
                cancel_at_period_end=False,
                proration_behavior='create_prorations',
                items=[
                    {
                        'id': subscription['items']['data'][0].id,
                        'price': price_obj.id,
                    }
                ]
            )
            djstripe_subscription = Subscription.sync_from_stripe_data(change_subscription)
            user.stripe_subscription = djstripe_subscription
            user.is_paysubscribed = new_tier
            user.paysubscribe_changed = timezone.now()

            user.save()

            user_context = model_to_dict(user, exclude=['groups', 'password', 'user_permissions'])
            request_context = { 'request': request }
            template = loader.get_template('payments/email/subscribe_change.txt')
            context = {**user_context, **request_context}
            html_message = template.render(context)
            mail.send(
                user.email,
                settings.EMAIL_ADDR,
                subject='Subscription change confirmation for ' + request.get_host(),
                html_message=html_message
            )

            return render(request, 'payments/subscribe_complete.html')
        else:
            return render(request, '400.html')
    elif new_tier == '0' and request.user.is_paysubscribed > 0:
        try:
            user = request.user
            subscription_obj = Subscription.objects.get(djstripe_id=user.stripe_subscription_id)
            subscription = stripe.Subscription.retrieve(subscription_obj.id)

        except Exception:
            user = None

        if user and subscription:
            change_subscription = stripe.Subscription.modify(
                subscription.id,
                cancel_at_period_end=True,
            )
            djstripe_subscription = Subscription.sync_from_stripe_data(change_subscription)
            user.stripe_subscription = djstripe_subscription
            user.paysubscribe_changed = timezone.now()

            user.save()

            user_context = model_to_dict(user, exclude=['groups', 'password', 'user_permissions'])
            request_context = { 'request': request }
            template = loader.get_template('payments/email/subscribe_change.txt')
            context = {**user_context, **request_context}
            html_message = template.render(context)
            mail.send(
                user.email,
                settings.EMAIL_ADDR,
                subject='Subscription change confirmation for ' + request.get_host(),
                html_message=html_message
            )

            return render(request, 'payments/cancel_subscription.html')
        else:
            return render(request, '400.html')
    else:
        return render(request, '400.html')


@transaction.atomic
@login_required
@csrf_exempt
def subscribe_card_change_complete(request, *args, **kwargs):

    if settings.STRIPE_LIVE_MODE == 'True':
        stripe.api_key = settings.STRIPE_LIVE_SECRET_KEY
    else:
        stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

    if kwargs['session_id']:
        try:
            user = request.user
            data = stripe.checkout.Session.retrieve(
                kwargs['session_id'], 
                expand=['setup_intent', 'setup_intent.customer', 'setup_intent.payment_method']
            )
            token = data.metadata.token

        except Exception:
            user = None
        if user and cardchange_token.check_token(user, token):

            customer_obj = data.setup_intent.customer
            payment_obj = data.setup_intent.payment_method
            subscription = Subscription.objects.get(id=data.setup_intent.metadata.subscription_id)

            djstripe_payment = PaymentMethod.sync_from_stripe_data(payment_obj)
            user.stripe_paymentmethod = djstripe_payment

            djstripe_customer = Customer.sync_from_stripe_data(customer_obj)
            user.stripe_customer = djstripe_customer

            subscription.default_payment_method_id = payment_obj.id

            user.paysubscribe_changed = timezone.now()

            subscription.save()
            user.save()

            return render(request, 'payments/card_change_complete.html')
        else:
            return render(request, '400.html')
    else:
        return render(request, '400.html')


@transaction.atomic
@login_required
@csrf_exempt
def subscribe_complete(request, *args, **kwargs):

    if settings.STRIPE_LIVE_MODE == 'True':
        stripe.api_key = settings.STRIPE_LIVE_SECRET_KEY
    else:
        stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

    if kwargs['session_id']:
        try:
            user = request.user
            data = stripe.checkout.Session.retrieve(
                kwargs['session_id'], 
                expand=['subscription', 'subscription.default_payment_method', 'subscription.plan.product', 'customer']
            )
            token = data.metadata.token
        except Exception:
            user = None
        if user and subscribe_token.check_token(user, token):

            customer_obj = data.customer
            subscription_obj = data.subscription
            payment_obj = data.subscription.default_payment_method
            product_obj = data.subscription.plan.product

            djstripe_payment = PaymentMethod.sync_from_stripe_data(payment_obj)
            user.stripe_paymentmethod = djstripe_payment

            djstripe_customer = Customer.sync_from_stripe_data(customer_obj)
            user.stripe_customer = djstripe_customer

            djstripe_subscription = Subscription.sync_from_stripe_data(subscription_obj)
            user.stripe_subscription = djstripe_subscription

            djstripe_tierlevel = data.subscription.plan.product.metadata.tier
            user.is_paysubscribed = djstripe_tierlevel

            user.paysubscribe_changed = timezone.now()

            user.save()

            user_context = model_to_dict(user, exclude=['groups', 'password', 'user_permissions'])
            request_context = { 'request': request }
            template = loader.get_template('payments/email/subscribe_message.txt')
            context = {**user_context, **request_context}
            html_message = template.render(context)
            mail.send(
                user.email,
                settings.EMAIL_ADDR,
                subject='Thanks for becoming a patron of ' + request.get_host(),
                html_message=html_message
            )

            return render(request, 'payments/subscribe_complete.html')
        else:
            return render(request, '400.html')
    else:
        return render(request, '400.html')


@login_required
@csrf_exempt
def subscribe_canceled(request):
    return render(request, 'payments/canceled.html')


@login_required
@csrf_exempt
def subscribe_card_change_canceled(request):
    return render(request, 'payments/card_change_canceled.html')


@login_required
def subscribe_new(request):

    return render(request, 'payments/subscribe.html', {
        'products': Product.objects.all().filter(type='service').exclude(metadata__isnull=True).order_by('metadata')
    })


@login_required
def subscribe_update(request):

    try: 
        tier_gte_objects = TierEqualOrGreater.objects.all()
    except:
        tier_gte_objects = None

    try:
        tier_eq_objects = TierEqual.objects.all()
    except:
        tier_eq_objects = None

    self = request

    if tier_gte_objects:
        user_gte_tiers = []
        for obj in tier_gte_objects:
            if obj.test_user(self):
                user_gte_tiers += [obj.segment_id]

    if tier_eq_objects:
        user_eq_tiers = []
        for obj in tier_eq_objects:
            if obj.test_user(self):
                user_eq_tiers += [obj.segment_id]

    private_queryset_pages = PodcastContentPage.objects.none()

    if tier_gte_objects and tier_eq_objects:
        for tier in user_gte_tiers:
            private_queryset_pages |= TierEqualOrGreater.segment.get_queryset().get(id=tier).get_used_pages().values_list('variant_id')
        for tier in user_eq_tiers:
            private_queryset_pages |= TierEqual.segment.get_queryset().get(id=tier).get_used_pages().values_list('variant_id')
    elif tier_gte_objects and not tier_eq_objects:
        for tier in user_gte_tiers:
            private_queryset_pages |= TierEqualOrGreater.segment.get_queryset().get(id=tier).get_used_pages().values_list('variant_id')
    elif tier_eq_objects and not tier_gte_objects:
        for tier in user_eq_tiers:
            private_queryset_pages |= TierEqual.segment.get_queryset().get(id=tier).get_used_pages().values_list('variant_id')
    else:
        private_queryset_pages = None

    if settings.DEBUG and settings.DATABASES['default']['ENGINE'] =='django.db.backends.sqlite3':
        try:
            podcast_queryset = PodcastContentPage.objects.filter(Q(id__in=private_queryset_pages)).order_by('parent_page').distinct()
        except:
            podcast_queryset = None
    else:
        try:
            podcast_queryset = PodcastContentPage.objects.filter(Q(id__in=private_queryset_pages)).order_by('parent_page').distinct('parent_page')
        except:
            podcast_queryset = None
    if settings.DEBUG and settings.DATABASES['default']['ENGINE'] =='django.db.backends.sqlite3':
        try:
            article_queryset = ArticleContentPage.objects.filter(Q(id__in=private_queryset_pages)).order_by('parent_page').distinct()
        except:
            article_queryset = None
    else:
        try:
            article_queryset = ArticleContentPage.objects.filter(Q(id__in=private_queryset_pages)).order_by('parent_page').distinct('parent_page')
        except:
            article_queryset = None

    token = premium_token.make_token(request.user)
    uid = urlsafe_base64_encode(force_bytes(request.user.email))

    return render(request, 'payments/update_subscription.html', {
        'products': Product.objects.all().filter(type='service').exclude(metadata__isnull=True).order_by('metadata'),
        'token': token,
        'uid': uid,
        'podcasts': podcast_queryset if podcast_queryset else None,
        'articles': article_queryset if article_queryset else None,
    })


@transaction.atomic
@user_passes_test(lambda u: u.is_superuser)
def reset_user(request, uidb64):
    try:
        user_email = urlsafe_base64_decode(uidb64).decode()
        user = UserModel.objects.get(email=user_email)
    except:
        user = None
    if user:
        user.uuid = uuid.uuid4()
        user.download_resets += 1
        user.save()
        DownloadAdmin.model.objects.filter(user_id=user.id).delete()
        user_context = model_to_dict(user, exclude=['groups', 'password', 'user_permissions'])
        request_context = { 'request': request }
        template = loader.get_template('account/email/reset_message.txt')
        context = {**user_context, **request_context}
        html_message = template.render(context)
        mail.send(
            user.email,
            settings.EMAIL_ADDR,
            subject='Premium download link reset on ' + request.get_host(),
            html_message=html_message
        )
    url_helper = DownloadAdmin().url_helper
    index_url = url_helper.index_url
    return HttpResponseRedirect(index_url)
