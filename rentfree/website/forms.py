from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _
from djstripe.models.core import Customer
from djstripe.models.billing import Subscription
from djstripe.models.payment_methods import PaymentMethod
from modelcluster.fields import ParentalKey
from users.models import CustomUserProfile
from wagtail.contrib.forms.models import AbstractFormField
from wagtail.users.forms import UserEditForm, UserCreationForm


FORM_FIELD_CHOICES = (
    (_('Text'), (
        ('singleline', _('Single line text')),
        ('multiline', _('Multi-line text')),
        ('email', _('Email')),
        ('number', _('Number - only allows integers')),
        ('url', _('URL')),
    ),),
    (_('Choice'), (
        ('checkboxes', _('Checkboxes')),
        ('dropdown', _('Drop down')),
        ('radio', _('Radio buttons')),
        ('multiselect', _('Multiple select')),
        ('checkbox', _('Single checkbox')),
    ),),
    (_('Date & Time'), (
        ('date', _('Date')),
        ('time', _('Time')),
        ('datetime', _('Date and time')),
    ),),
    (_('Other'), (
        ('hidden', _('Hidden field')),
    ),),
)


class FormPageField(AbstractFormField):

    class Meta:
        ordering = ['sort_order']

    field_type = models.CharField(
        verbose_name=_('field type'),
        max_length=16,
        choices=FORM_FIELD_CHOICES,
        blank=False
    )
    page = ParentalKey(
        'BasicFormPage',
        related_name='form_fields'
    )


# Date

class DateInput(forms.DateInput):
    template_name = 'website/formfields/date.html'


class DateField(forms.DateField):
    widget = DateInput()


# Datetime

class DateTimeInput(forms.DateTimeInput):
    template_name = 'website/formfields/datetime.html'


class DateTimeField(forms.DateTimeField):
    widget = DateTimeInput()
    input_formats = ['%Y-%m-%dT%H:%M', '%m/%d/%Y %I:%M %p', '%m/%d/%Y %I:%M%p', '%m/%d/%Y %H:%M']


# Time

class TimeInput(forms.TimeInput):
    template_name = 'website/formfields/time.html'


class TimeField(forms.TimeField):
    widget = TimeInput()
    input_formats = ['%H:%M', '%I:%M %p', '%I:%M%p']


class SearchForm(forms.Form):
    s = forms.CharField(
        widget=forms.TextInput,
        max_length=255,
        required=False,
        label=_('Search'),
    )
    t = forms.CharField(
        widget=forms.HiddenInput,
        max_length=255,
        required=False,
        label=_('Page type'),
    )
    

def get_page_model_choices():
    """
    Returns a list of tuples of all creatable pages
    in the format of ("Web Page", "WebPage")
    """
    from website.models import get_page_models
    return (
        (
            page.__name__,
            re.sub(
                r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))',
                r' \1',
                page.__name__
            )
        ) for page in get_page_models() if page.is_creatable
    )


class ReadOnlyFieldsMixin(object):
    readonly_fields = ()

    def __init__(self, *args, **kwargs):
        super(ReadOnlyFieldsMixin, self).__init__(*args, **kwargs)
        for field in (field for name, field in self.fields.items() if
                      name in self.readonly_fields):
            field.widget.attrs['disabled'] = 'true'
            field.required = False

    def clean(self):
        for f in self.readonly_fields:
            self.cleaned_data.pop(f, None)
        return super(ReadOnlyFieldsMixin, self).clean()


class CustomUserEditForm(ReadOnlyFieldsMixin, UserEditForm):

    readonly_fields = ('is_paysubscribed', 'is_newuserprofile', 'stripe_customer', 'stripe_subscription', 'stripe_paymentmethod', 'download_resets')

    user_name = forms.CharField(required=False, label=_('User name'))
    url = forms.URLField(required=False, label=_('Bio URL'))
    is_mailsubscribed = forms.BooleanField(required=False, label=_('Email alerts?'))
    is_paysubscribed = forms.IntegerField(required=False, label=_('Subscriber tier'))
    is_smssubscribed = forms.BooleanField(required=False, label=_('SMS alerts?'))
    is_newuserprofile = forms.BooleanField(required=False, label=_('Initial profile?'))
    stripe_customer = forms.ModelChoiceField(queryset=Customer.objects, required=False, label=_('Customer id'))
    stripe_subscription = forms.ModelChoiceField(queryset=Subscription.objects, required=False, label=_('Subscription id'))
    stripe_paymentmethod = forms.ModelChoiceField(queryset=PaymentMethod.objects, required=False, label=_('Pay method id'))
    download_resets = forms.CharField(required=False, label=_('Link resets'), help_text=_("How many times you've reset the user's download links for causing excessive downloads from this account."))

class CustomUserCreationForm(ReadOnlyFieldsMixin, UserCreationForm):

    user_name = forms.CharField(required=False, label=_('User name'))
    url = forms.URLField(required=False, label=_('Bio URL'))
    is_mailsubscribed = forms.BooleanField(required=False, label=_('Email alerts?'))
    is_paysubscribed = forms.IntegerField(required=False, label=_('Subscriber tier'))
    is_smssubscribed = forms.BooleanField(required=False, label=_('SMS alerts?'))
    is_newuserprofile = forms.BooleanField(required=True, label=_('Has edited profile?'))
