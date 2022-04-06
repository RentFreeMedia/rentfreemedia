import uuid

from comment.models.comments import Comment
from comment.models.blocker import BlockedUser, BlockedUserHistory
from comment.models.flags import Flag
from comment.models.followers import Follower
from comment.models.reactions import Reaction
from datetime import datetime
from dbtemplates.models import Template
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django import forms
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_summernote.widgets import SummernoteWidget
from django.urls import reverse
from django.utils.html import mark_safe
from django.utils.translation import ugettext_lazy as _
from djstripe.models.billing import Subscription, Invoice, Coupon
from djstripe.models.core import Product
from website.edit_handlers import (
    ReadOnlyPanel,
    SubscriptionPermissionHelper,
    CommentPermissionHelper,
    EmailLogPermissionHelper,
    DripLogPermissionHelper,
    DownloadPermissionHelper
)
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.core import hooks
from wagtail.core.models import UserPagePermissionsProxy, get_page_models
from wagtailcache.cache import clear_cache
from wagtail.contrib.modeladmin.options import (
    ModelAdmin, ModelAdminGroup, modeladmin_register)
from wagtail.contrib.modeladmin.views import CreateView, InspectView
from wagtail.images import image_operations
from website.models.media import Download
from website.models.settings import GeneralSettings
from website.wagtail_flexible_forms.wagtail_hooks import (
    FormAdmin as FlexibleformFormAdmin,
    SubmissionAdmin as FlexibleformSubmissionAdmin
)
from willow.plugins.pillow import PillowImage

from drip.models import Drip, SentDrip, QuerySetRule
from post_office.models import Log, Email, EmailTemplate
from post_office.admin import SubjectField, CommaSeparatedEmailWidget, get_message_preview


@hooks.register('after_create_page')
@hooks.register('after_edit_page')
def clear_wagtailcache(request, page):
    if page.live:
        clear_cache()

@hooks.register('filter_form_submissions_for_user')
def website_forms(user, editable_forms):
    from website.models.pages import FormPageMixin
    """
    Add our own WebsiteFormPage to editable_forms, since wagtail is unaware
    of its existance. Essentailly this is a fork of wagtail.contrib.forms.get_forms_for_user()
    and wagtail.contrib.forms.get_form_types()
    """
    form_models = [
        model for model in get_page_models()
        if issubclass(model, FormPageMixin)
    ]
    form_types = list(
        ContentType.objects.get_for_models(*form_models).values()
    )

    editable_forms = UserPagePermissionsProxy(user).editable_pages()
    editable_forms = editable_forms.filter(content_type__in=form_types)

    return editable_forms

@hooks.register('after_copy_page')
def new_page_guid(request, page, new_page):
    content_pages = ['PodcastContentIndexPage', 'ArticleContentIndexPage']
    if new_page.get_parent().specific._meta.object_name in content_pages:
        new_page.guid = uuid.uuid4()
        new_page.date_display = datetime.now()
        new_page.cover_image = None
        new_page.remote_media = None
        new_page.uploaded_media = None
        new_page.uploaded_media_type = None
        new_page.remote_media_type = None
        new_page.remote_media_size = None
        new_page.remote_media_thumbnail = None
        new_page.remote_media_duration = None
        new_page.og_image = None
        new_page.author.clear()
        new_page.contributor.clear()
        new_page.tags.clear()
        new_page.content_walls.clear()

        if new_page.get_parent().specific._meta.object_name == 'PodcastContentIndexPage' and page.specific.episode_number:
            new_page.episode_number += 1
    new_page.save_revision()


class SubmissionAdmin(FlexibleformSubmissionAdmin):

    def __init__(self, parent=None):
        from website.models.pages import SessionFormSubmission
        self.model = SessionFormSubmission
        super().__init__(parent=parent)


class FormAdmin(FlexibleformFormAdmin):
    list_display = ('title', 'action_links')

    def all_submissions_link(self, obj, label=_('See all submissions'),
                             url_suffix=''):
        return '<a href="%s?page_id=%s%s">%s</a>' % (
            reverse(WebsiteSubmissionAdmin().url_helper.get_action_url_name('index')),
            obj.pk, url_suffix, label)
    all_submissions_link.short_description = ''
    all_submissions_link.allow_tags = True

    def action_links(self, obj):
        from website.models.pages import BasicFormPage, StreamFormPage
        actions = []
        if issubclass(type(obj.specific), BasicFormPage):
            actions.append(
                '<a href="{0}">{1}</a>'.format(reverse(
                    'wagtailforms:list_submissions',
                    args=(obj.pk,)),
                    _('See all Submissions')
                )
            )
            actions.append(
                '<a href="{0}">{1}</a>'.format(
                    reverse("wagtailadmin_pages:edit", args=(obj.pk,)), _("Edit this form page")
                )
            )
        elif issubclass(type(obj.specific), StreamFormPage):
            actions.append(self.unprocessed_submissions_link(obj))
            actions.append(self.all_submissions_link(obj))
            actions.append(self.edit_link(obj))

        return mark_safe("<br />".join(actions))


class CommentAdmin(ModelAdmin):

    model = Comment
    menu_icon = 'form'
    menu_label = 'Comments'
    list_display = ('user', 'content_type', 'posted', 'edited')
    search_fields = ['user__user_name', 'email', 'content', 'posted', 'edited']
    permission_helper_class = CommentPermissionHelper

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'

    panels = [
        MultiFieldPanel(
            [
                ReadOnlyPanel('user'),
                ReadOnlyPanel('email'),
                ReadOnlyPanel('parent'),
                ReadOnlyPanel('content_type'),
            ],
            _('Comment data')
        ),
        MultiFieldPanel(
            [
                ReadOnlyPanel('content'),
            ],
            _('Comment content')
        )
    ]


class CommentBlockedUserAdmin(ModelAdmin):
    model = BlockedUser
    menu_icon = 'user'
    menu_label = 'Blocked Users'
    list_display = ('user', 'email', 'blocked')
    search_fields = ['user', 'email']
    list_filter = ['blocked']
    permission_helper_class = CommentPermissionHelper

    class Meta:
        verbose_name = 'Blocked User'
        verbose_name_plural = 'Blocked Users'

    panels = [
        MultiFieldPanel(
            [
                ReadOnlyPanel('user', classname='User'),
                ReadOnlyPanel('email', classname='Email'),
                FieldPanel('blocked', classname='Blocked'),
            ],
            _('Blocked user data')
        )
    ]

class CommentBlockedUserHistory(ModelAdmin):
    model = BlockedUserHistory
    menu_icon = 'date'
    menu_label = 'Blocked User History'
    list_display = ('blocked_user', 'blocker', 'reason', 'state', 'date')
    search_fields = ['blocked_user', 'blocker', 'reason']
    list_filter = ['state', 'blocker']
    permission_helper_class = CommentPermissionHelper

    class Meta:
        verbose_name = 'Blocked User History'
        verbose_name_plural = 'Blocked User Histories'

    panels = [
        MultiFieldPanel(
            [
                ReadOnlyPanel('blocked_user'),
                ReadOnlyPanel('blocker'),
                ReadOnlyPanel('reason'),
                ReadOnlyPanel('state'),
                ReadOnlyPanel('date'),
            ],
            _('Blocked user history data')
        )
    ]

class CommentFlags(ModelAdmin):
    model = Flag
    menu_icon = 'cross'
    menu_label = 'Flags'
    list_display = ('id', 'count', 'state', 'moderator')
    search_fields = ['moderator', 'commment__content']
    list_filter = ['state', 'moderator']
    permission_helper_class = CommentPermissionHelper

    class Meta:
        verbose_name = 'Comment Flag'
        verbose_name_plural = 'Comment Flags'

    panels = [
        MultiFieldPanel(
            [
                ReadOnlyPanel('count', classname='Count'),
                ReadOnlyPanel('state', classname='State'),
                ReadOnlyPanel('moderator', classname='Moderator'),
                ReadOnlyPanel('comment', classname='Comment'),
            ],
            _('Comment flag data')
        )
    ]

class CommentFollowers(ModelAdmin):
    model = Follower
    menu_icon = 'group'
    menu_label = 'Comment Followers'
    list_display = ('email', 'username', 'content_type', 'content_object')
    search_fields = ['username', 'email']
    permission_helper_class = CommentPermissionHelper

    class Meta:
        verbose_name = 'Comment Follower'
        verbose_name_plural = 'Comment Followers'

    panels = [
        MultiFieldPanel(
            [
                ReadOnlyPanel('email'),
                ReadOnlyPanel('username'),
                ReadOnlyPanel('content_type'),
                ReadOnlyPanel('content_object'),
            ],
            _('Comment follower data')
        )
    ]


class CommentReactions(ModelAdmin):
    model = Reaction
    menu_icon = 'tick'
    menu_label = 'Comment Reactions'
    list_display = ('comment', 'likes', 'dislikes')
    search_fields = ['comment__content']
    list_filter = ['likes', 'dislikes']
    permission_helper_class = CommentPermissionHelper

    class Meta:
        verbose_name = 'Comment Reaction'
        verbose_name_plural = 'Comment Reactions'

    panels = [
        MultiFieldPanel(
            [
                ReadOnlyPanel('comment', classname='Comment'),
                ReadOnlyPanel('likes', classname='Likes'),
                ReadOnlyPanel('dislikes', classname='Dislikes'),
            ],
            _(' Comment reaction data')
        )
    ]

class DownloadAdmin(ModelAdmin):
    model = Download
    menu_icon = 'download'
    menu_label = 'Media Downloads'
    list_display = ('user', 'media', 'download_count', 'last')
    date_hierarchy = 'last'
    ordering = ['-download_count']
    edit_template_name = 'modeladmin/website/downloadadmin/edit.html'
    permission_helper_class = DownloadPermissionHelper

    class Meta:
        verbose_name = 'Media Download'
        verbose_name_plural = 'Media Downloads'

    panels = [
        MultiFieldPanel(
            [
                ReadOnlyPanel('user', classname='User'),
                ReadOnlyPanel('media', classname='Media'),
                ReadOnlyPanel('download_count', classname='Count'),
                ReadOnlyPanel('last', classname='Last'),
            ],
        )
    ]


class HTMLTemplateAdmin(ModelAdmin):
    model = Template
    menu_icon = 'code'
    menu_label = 'HTML Templates'
    menu_order = 1200
    list_display = ('name', 'creation_date', 'last_changed')
    date_hierarchy = 'last_updated'

    class Meta:
        verbose_name = 'HTML Template'
        verbose_name_plural = 'HTML Templates'

    panels = [
        MultiFieldPanel(
            [
                FieldPanel('name'),
                FieldPanel('content'),
            ],
            _('Template name and content')
        )
    ]


class SubscriptionAdmin(ModelAdmin):
    model = Subscription
    menu_icon = 'tick'
    menu_label = 'Subscriptions'
    list_display = ('djstripe_id', 'id', 'customer', 'plan_id', 'status', 'cancel_at_period_end', 'current_period_end')
    search_fields = ['customer__name', 'customer__email', 'status', 'plan__amount', 'discount']
    date_hierarchy = 'last_updated'
    list_filter = ['status', 'plan__amount']
    permission_helper_class = SubscriptionPermissionHelper

    class Meta:
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'

    panels = [
        MultiFieldPanel(
            [
                ReadOnlyPanel('djstripe_id', 'Id'),
                ReadOnlyPanel('id', 'Stripe id'),
                ReadOnlyPanel('plan_id', 'Plan id'),
                ReadOnlyPanel('customer', 'Customer'),
            ],
            _('User and Plan Info')
        ),
         MultiFieldPanel(
            [
                ReadOnlyPanel('status', 'Status'),
                ReadOnlyPanel('cancel_at_period_end', 'Set to cancel?'),
                ReadOnlyPanel('start_date', 'Start date'),
                ReadOnlyPanel('current_period_end', 'Cycle end date'),
                ReadOnlyPanel('djstripe_updated', 'Last updated'),
                ReadOnlyPanel('canceled_at', 'Date canceled')
            ],
            _('Status and Renewal Info')
        ),
    ]


class InvoiceAdmin(ModelAdmin):
    model = Invoice
    menu_icon = 'form'
    menu_label = 'Invoices'
    list_display = ('djstripe_id', 'id', 'customer_name', 'customer_email', 'attempt_count', 'created')
    search_fields = ['customer_name', 'customer_email', 'status', 'number', 'discount']
    date_hierarchy = 'djstripe_updated'
    list_filter = ['status', 'subtotal']
    permission_helper_class = SubscriptionPermissionHelper

    class Meta:
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'

    panels = [
        MultiFieldPanel(
            [
                ReadOnlyPanel('djstripe_id', 'Id'),
                ReadOnlyPanel('id', 'Stripe id'),
                ReadOnlyPanel('customer_name', 'Customer name'),
                ReadOnlyPanel('customer_email', 'Customer email'),
            ],
            _('Customer Info')
        ),
         MultiFieldPanel(
            [
                ReadOnlyPanel('created', 'Created'),
                ReadOnlyPanel('number', 'Invoice number'),
                ReadOnlyPanel('billing_reason', 'Summary'),
                ReadOnlyPanel('subtotal', 'Subtotal'),
                ReadOnlyPanel('tax', 'Tax'),
                ReadOnlyPanel('total', 'Total'),
            ],
            _('Invoice Details')
        ),
            MultiFieldPanel(
            [
                ReadOnlyPanel('status', 'Status'),
                ReadOnlyPanel('attempt_count', 'Charge attempts'),
                ReadOnlyPanel('amount_paid', 'Amount paid'),
                ReadOnlyPanel('ending_balance', 'Ending balance'),
                ReadOnlyPanel('invoice_pdf', 'PDF link'),
                ReadOnlyPanel('hosted_invoice_url', 'HTML link')
            ],
            _('Status')
        ),
    ]


class ProductAdmin(ModelAdmin):
    model = Product
    menu_icon = 'pick'
    menu_label = 'Products'
    list_display = ('djstripe_id', 'id', 'name', 'metadata', 'active', 'created')
    search_fields = ['description', 'name', 'metadata', 'type']
    date_hierarchy = 'djstripe_updated'
    list_filter = ['type']
    permission_helper_class = SubscriptionPermissionHelper

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    panels = [
        MultiFieldPanel(
            [
                ReadOnlyPanel('djstripe_id', 'Id'),
                ReadOnlyPanel('id', 'Stripe id'),
                ReadOnlyPanel('name', 'Name'),
                ReadOnlyPanel('description', 'Description'),
                ReadOnlyPanel('type', 'Type'),
            ],
            _('Product Info')
        ),
         MultiFieldPanel(
            [
                ReadOnlyPanel('active', 'Status'),
                ReadOnlyPanel('created', 'Created'),
                ReadOnlyPanel('djstripe_updated', 'Updated'),
                ReadOnlyPanel('deactivate_on', 'Deactivate date'),
            ],
            _('Status')
        ),
    ]


class CouponAdmin(ModelAdmin):
    model = Coupon
    menu_icon = 'tag'
    menu_label = 'Coupons'
    list_display = ('djstripe_id', 'id', 'name', 'amount_off', 'percent_off', 'times_redeemed', 'created')
    search_fields = ['name', 'amount_off', 'percent_off', 'duration', 'duration_in_months', 'subscription__discount']
    date_hierarchy = 'djstripe_updated'
    list_filter = ['duration']
    permission_helper_class = SubscriptionPermissionHelper

    class Meta:
        verbose_name = 'Coupon'
        verbose_name_plural = 'Coupons'

    panels = [
        MultiFieldPanel(
            [
                ReadOnlyPanel('djstripe_id', 'Id'),
                ReadOnlyPanel('name', 'Name'),
                ReadOnlyPanel('description', 'Description'),
                ReadOnlyPanel('amount_off', 'Amount off'),
                ReadOnlyPanel('percent_off', 'Percent off'),
                ReadOnlyPanel('duration', 'Duration'),
            ],
            _('Coupon Info')
        ),
         MultiFieldPanel(
            [
                ReadOnlyPanel('created', 'Created'),
                ReadOnlyPanel('djstripe_updated', 'Updated'),
                ReadOnlyPanel('times_redeemed', 'Times redeemed'),
                ReadOnlyPanel('max_redemptions', 'Max redemptions'),
                ReadOnlyPanel('redeem_by', 'Redeem by'),
            ],
            _('Status')
        ),
    ]


class EmailAdmin(ModelAdmin):
    model = Email
    menu_icon = 'group'
    menu_label = 'Send Emails'
    list_display = ('to', 'group', 'subject', 'template', 'status', 'last_updated')
    search_fields = ['group__name', 'to', 'template__name']
    date_hierarchy = 'last_updated'
    list_filter = ['status']

    class Meta:
        verbose_name = "Email"
        verbose_name_plural = "Emails"

    panels = [
        MultiFieldPanel(
            [
                FieldPanel('from_email'),
                FieldPanel('to', widget=CommaSeparatedEmailWidget),
                FieldPanel('group'),
                FieldPanel('template'),
            ],
            _('Email Address Fields'),
        ),
        MultiFieldPanel(
            [
                FieldPanel('status'),
                FieldPanel('priority'),
                FieldPanel('scheduled_time'),
            ],
            _('Scheduling Options'),
        ),
        MultiFieldPanel(
            [
                FieldPanel('subject', widget=SubjectField),
                FieldPanel('message', widget=forms.Textarea),
                FieldPanel('html_message', widget=SummernoteWidget())
            ],
            _('Content'),
            classname="collapsible collapsed"
        ),
        MultiFieldPanel(
            [
                FieldPanel('cc', widget=CommaSeparatedEmailWidget),
                FieldPanel('bcc', widget=CommaSeparatedEmailWidget),
                FieldPanel('context'),
                FieldPanel('headers'),
                FieldPanel('backend_alias')
            ],
            _('Uncommon Options'),
            classname="collapsible collapsed"
        )
    ]

class EmailTemplateAdmin(ModelAdmin):
    model = EmailTemplate
    menu_icon = 'edit'
    menu_label = 'Email Templates'
    list_display = ('name', 'created', 'description', 'subject')
    search_fields = ['name', 'description', 'subject', 'content']

    panels = [
        MultiFieldPanel(
            [
                FieldPanel('name'),
                FieldPanel('description', widget=SubjectField),
                FieldPanel('subject', widget=SubjectField),
                FieldPanel('html_content', widget=SummernoteWidget()),
                FieldPanel('content', widget=forms.Textarea),
            ],
            _('Email Template'),
        )
    ]


class EmailLogAdmin(ModelAdmin):
    model = Log
    menu_icon = 'list-ul'
    menu_label = 'Failed Email Logs'
    list_display = ('email', 'status', get_message_preview, 'date')
    list_filter = ['status']
    permission_helper_class = EmailLogPermissionHelper

    panels = [
        MultiFieldPanel(
            [
                FieldPanel('status'),
                FieldPanel('exception_type'),
                FieldPanel('message'),
            ],
            _('Email Log'),
        )
    ]

class DripAdminCreateView(CreateView):
    def get_instance(self):
        instance = super().get_instance()
        # default values for first query rules InlinePanel to only match subscribed users
        if instance.queryset_rules.exists():
            pass
        else:
            instance.queryset_rules = [
                QuerySetRule(method_type='filter', field_name='is_mailsubscribed', lookup_type='exact', rule_type='and', field_value=1, sort_order=0)
            ]
        return instance

class DripAdminInspectView(InspectView):
    
    def get_context_data(self, **kwargs):
        
        context = {
            'fields': self.get_fields_dict(),
            'buttons': self.button_helper.get_buttons_for_obj(
                self.instance, exclude=['inspect']),
        }
        context.update(kwargs)

        return super().get_context_data(**context)

    def view_drip_email(self, request, drip_id, user_id):
        into_past = 4
        into_future = 7

        drip = get_object_or_404(Drip, id=drip_id)
        User = get_user_model()
        user = get_object_or_404(User, id=user_id)

        html, mime = self.get_mime_html(drip, user)

        return HttpResponse(html, content_type=mime)

    def get_fields(self):
        return [(field.name, field.value_to_string(self)) for field in self._meta.fields]


class DripAdmin(ModelAdmin):
    model = Drip
    menu_icon = 'cogs'
    menu_label = 'Drip Email'
    list_display = ('id', 'name', 'subject_template', 'enabled', 'lastchanged')
    create_view_class = DripAdminCreateView
    inspect_view_class = DripAdminInspectView
    inspect_view_enabled = True
    inspect_template_name = 'modeladmin/website/dripadmin/inspect.html'
    inspect_view_fields_exclude = ('id', 'name', 'date', 'from_email', 'from_email_name', 'subject_template', 'body_html_template', 'queryset_rules', 'message_class')

    panels = [
        MultiFieldPanel(
            [
                FieldPanel('name', widget=SubjectField),
                FieldPanel('enabled'),
                FieldPanel('from_email', widget=SubjectField),
                FieldPanel('from_email_name', widget=SubjectField),
                FieldPanel('subject_template', widget=SubjectField),
                FieldPanel('body_html_template', widget=SummernoteWidget()),
                InlinePanel('queryset_rules', label='Query Set Rules'),
            ],
            _('Drip Admin'),
        )
    ]


class SentDripAdmin(ModelAdmin):
    model = SentDrip
    menu_icon = 'list-ul'
    menu_label = 'Drip Email Logs'
    list_display = ('id', 'drip', 'subject', 'user', 'date')
    permission_helper_class = DripLogPermissionHelper

    panels = [
        MultiFieldPanel(
            [
                FieldPanel('subject', widget=SubjectField),
                FieldPanel('body', widget=SummernoteWidget()),
                FieldPanel('from_email', widget=SubjectField),
                FieldPanel('from_email_name', widget=SubjectField),
            ],
            _('Sent Drip Admin'),
        )
    ]

class GrayscaleOperation(image_operations.FilterOperation):
    def construct(self):
        pass

    def run(self, willow, image, env):
        from PIL import ImageEnhance
        img_enh = ImageEnhance.Color(willow.get_pillow_image())
        image_gray = img_enh.enhance(0.0)
        return PillowImage(image_gray)

@hooks.register('register_image_operations')
def register_image_operations():
    return [
        ('original', image_operations.DoNothingOperation),
        ('fill', image_operations.FillOperation),
        ('min', image_operations.MinMaxOperation),
        ('max', image_operations.MinMaxOperation),
        ('width', image_operations.WidthHeightOperation),
        ('height', image_operations.WidthHeightOperation),
        ('grayscale', GrayscaleOperation),
    ]


class EmailGroup(ModelAdminGroup):
    menu_label = 'Email'
    menu_icon = 'mail'
    menu_order = 300
    items = (EmailTemplateAdmin, EmailAdmin, EmailLogAdmin, DripAdmin, SentDripAdmin)


class SubscriptionGroup(ModelAdminGroup):
    menu_label = 'Subscriptions'
    menu_icon = 'tick'
    menu_order = 1000
    items = (SubscriptionAdmin, InvoiceAdmin, ProductAdmin, CouponAdmin, DownloadAdmin)

class CommentGroup(ModelAdminGroup):
    menu_label = 'Comments'
    menu_icon = 'group'
    menu_order = 1100
    items = (CommentAdmin, CommentFlags, CommentBlockedUserAdmin, CommentBlockedUserHistory, CommentFollowers, CommentReactions)

EmailTemplate._meta.get_field('html_content').default = '<br /><br /><p style="text-align:center;font-size:small;">Click <a href="https://{{ unsubscribe }}">here</a> to unsubscribe from future emails.</p>'
EmailTemplate._meta.get_field('content').default = '\n\nClick the following link to unsubscribe from future emails: \nhttps://{{ unsubscribe }}'
try:
    default_email = GeneralSettings.objects.first()
except:
    default_email = None
if default_email:
    Email._meta.get_field('from_email').default = default_email.from_email
else:
    Email._meta.get_field('from_email').default = settings.DEFAULT_FROM_EMAIL

modeladmin_register(CommentGroup)
modeladmin_register(HTMLTemplateAdmin)
modeladmin_register(EmailGroup)
modeladmin_register(SubscriptionGroup)
