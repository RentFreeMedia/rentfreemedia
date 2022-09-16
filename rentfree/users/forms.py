import l18n
from operator import itemgetter
from django import forms
from django.forms import fields
from django.forms import widgets
from betterforms.multiform import MultiModelForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.db.models.fields import BLANK_CHOICE_DASH
from django.utils.translation import ugettext_lazy as _
from wagtail.admin.localization import get_available_admin_time_zones
from wagtail.contrib.forms.models import AbstractFormField
from wagtail.users.models import UserProfile
from users.models import CustomUserProfile
from phonenumber_field.widgets import PhoneNumberInternationalFallbackWidget
from allauth.account.adapter import get_adapter
from allauth.account import app_settings
from allauth.account import forms as allauthforms
from allauth.socialaccount import forms as allauthsocialforms
from allauth.utils import set_form_field_order

UserModel = get_user_model()

def _get_time_zone_choices():
    time_zones = []
    for tz in get_available_admin_time_zones():
        if 'US/' not in tz:
            time_zones.append((tz, str(l18n.tz_fullnames.get(tz, tz))))
        else:
            time_zones.append((tz, str(tz)))

    time_zones.sort(key=itemgetter(1))
    return BLANK_CHOICE_DASH + time_zones


class PasswordField(forms.CharField):
    def __init__(self, *args, **kwargs):
        render_value = kwargs.pop(
            "render_value", app_settings.PASSWORD_INPUT_RENDER_VALUE
        )
        kwargs["widget"] = forms.PasswordInput(
            render_value=render_value,
            attrs={"placeholder": 'Password', "class": "form-control"},
        )
        autocomplete = kwargs.pop("autocomplete", None)
        if autocomplete is not None:
            kwargs["widget"].attrs["autocomplete"] = autocomplete
        super(PasswordField, self).__init__(*args, **kwargs)


class SetPasswordField(PasswordField):
    def __init__(self, *args, **kwargs):
        kwargs["autocomplete"] = "new-password"
        super(SetPasswordField, self).__init__(*args, **kwargs)
        self.user = None

    def clean(self, value):
        value = super(SetPasswordField, self).clean(value)
        value = get_adapter().clean_password(value, user=self.user)
        return value


class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = UserModel
        fields = ('email',)


class CustomUserChangeForm(UserChangeForm):

    class Meta(UserChangeForm):
        model = UserModel
        fields = ('email',)


class InitialUserForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.Meta.required:
            self.fields[field].required = True

    class Meta:
        model = UserModel
        fields = ('first_name', 'last_name', 'user_name', 'is_mailsubscribed')
        required = ('user_name',)
        labels = {
            'user_name': _('User name'),
            'first_name': _('First name'),
            'last_name': _('Last name'),
            'is_mailsubscribed': _('Recieve notification and offer emails from us'),
        }
        widgets = {
            'user_name': widgets.TextInput(attrs={'placeholder': _('User name (public: visible on comments and replies)'),
                'autocomplete': 'username', 'class': 'form-control'}),
            'first_name': widgets.TextInput(attrs={'placeholder':_('First name (private: only visible to admins/staff)'), 
                'autocomplete': 'first name', 'class': 'form-control'}),
            'last_name': widgets.TextInput(attrs={'placeholder':_('Last name (private: only visible to admins/staff)'), 
                'autocomplete': 'last name', 'class': 'form-control'}),
            'is_mailsubscribed': widgets.CheckboxInput(attrs={'input_type': 'checkbox'}),
        }
        error_messages = {
            'user_name': {
                'max_length': _('15 characters or fewer.'),
                'invalid':_('Letters, digits, and the characters @ . + - _ only.'),
                'unique': _('A user with that username already exists.'),
            },
        }
        help_texts = {
            'user_name': None,
        }

class InitialUserProfileForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.Meta.required:
            self.fields[field].required = True

    class Meta:
        model = CustomUserProfile
        fields = ('phone',)
        required = ('')
        labels = {
            'phone': _('Phone number'),
        }
        widgets = {
            'phone': PhoneNumberInternationalFallbackWidget(
                attrs={'placeholder': _('Phone (private: only visible to admins/staff)'), 
                'autocomplete': 'tel', 'class': 'form-control', 'type': 'tel'}
            ),
        }
        error_messages = {
            'phone': {
                'invalid': _('Invalid phone number, double check your entry.'),
                'unique': _('A user with that phone number already exists.'),
            },
        }


class InitialWagtailProfileForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_avatar = self.instance.avatar

        for field in self.Meta.required:
            self.fields[field].required = True

    current_time_zone = fields.ChoiceField(label=_('Time zone'), 
        choices=_get_time_zone_choices, initial='US/Eastern', 
        required=True, widget=widgets.Select(attrs={'class': 'form-select'}))

    avatar = fields.ImageField(label=_('Profile picture'),
        required=False, widget=widgets.FileInput(attrs={'label': _('Choose file'),
        'class': 'form-control', 'type': 'file'}))

    class Meta:
        model = UserProfile
        fields = ('current_time_zone', 'avatar')
        required = ('current_time_zone',)

    def save(self, commit=True):
        if commit and self._original_avatar and (self._original_avatar != self.cleaned_data['avatar']):
            # Call delete() on the storage backend directly, as calling self._original_avatar.delete()
            # will clear the now-updated field on self.instance too
            try:
                self._original_avatar.storage.delete(self._original_avatar.name)
            except IOError:
                # failure to delete the old avatar shouldn't prevent us from continuing
                warnings.warn("Failed to delete old avatar file: %s" % self._original_avatar.name)

        super().save(commit=commit)


class InitialProfileMultiForm(MultiModelForm):

    form_classes = {
        'user': InitialUserForm,
        'base_userprofile': InitialUserProfileForm,
        'wagtail_userprofile': InitialWagtailProfileForm,
    }


class SubsequentUserForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.Meta.required:
            self.fields[field].required = True

    class Meta:
        model = UserModel
        fields = ('first_name', 'last_name', 'user_name', 'is_mailsubscribed')
        required = ('user_name',)
        labels = {
            'user_name': _('User name'),
            'first_name': _('First name'),
            'last_name': _('Last name'),
            'is_mailsubscribed': _('Recieve notification and offer emails from us'),
        }
        widgets = {
            'user_name': widgets.TextInput(attrs={'placeholder': _('User name (public: visible on comments and replies)'),
                'autocomplete': 'username', 'class': 'form-control'}),
            'first_name': widgets.TextInput(attrs={'placeholder':_('First name (private: only visible to admins/staff)'), 
                'autocomplete': 'first name', 'class': 'form-control'}),
            'last_name': widgets.TextInput(attrs={'placeholder':_('Last name (private: only visible to admins/staff)'), 
                'autocomplete': 'last name', 'class': 'form-control'}),
            'is_mailsubscribed': widgets.CheckboxInput(attrs={'input_type': 'checkbox'}),
        }
        error_messages = {
            'user_name': {
                'max_length': _('15 characters or fewer.'),
                'invalid':_('Letters, digits, and the characters @ . + - _ only.'),
                'unique': _('A user with that username already exists.'),
            },
        }
        help_texts = {
            'user_name': None,
        }


class SubsequentUserProfileForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.Meta.required:
            self.fields[field].required = True

    class Meta:
        model = CustomUserProfile
        fields = ('phone',)
        required = ('')
        labels = {
            'phone': _('Phone number'),
        }
        widgets = {
            'phone': PhoneNumberInternationalFallbackWidget(
                attrs={'placeholder': _('Phone (private: only visible to admins/staff)'), 
                'autocomplete': 'tel', 'class': 'form-control', 'type': 'tel'}
            ),
        }
        error_messages = {
            'phone': {
                'invalid': _('Invalid phone number, double check your entry.'),
                'unique': _('A user with that phone number already exists.'),
            },
        }


class SubsequentWagtailProfileForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_avatar = self.instance.avatar

        for field in self.Meta.required:
            self.fields[field].required = True

    current_time_zone = fields.ChoiceField(label=_('Time zone'), 
        choices=_get_time_zone_choices, initial='US/Eastern', 
        required=True, widget=widgets.Select(attrs={'class': 'form-select'}))

    avatar = fields.ImageField(label=_('Profile picture'),
        required=False, widget=widgets.FileInput(attrs={'label': _('Choose file'),
        'class': 'form-control', 'type': 'file'}))

    class Meta:
        model = UserProfile
        fields = ('current_time_zone', 'avatar')
        required = ('current_time_zone',)

    def save(self, commit=True):
        if commit and self._original_avatar and (self._original_avatar != self.cleaned_data['avatar']):
            # Call delete() on the storage backend directly, as calling self._original_avatar.delete()
            # will clear the now-updated field on self.instance too
            try:
                self._original_avatar.storage.delete(self._original_avatar.name)
            except IOError:
                # failure to delete the old avatar shouldn't prevent us from continuing
                warnings.warn("Failed to delete old avatar file: %s" % self._original_avatar.name)

        super().save(commit=commit)



class SubsequentProfileMultiForm(MultiModelForm):
    form_classes = {
        'wagtail_userprofile': SubsequentWagtailProfileForm,
        'base_userprofile': SubsequentUserProfileForm,
        'user': SubsequentUserForm
    }


class CustomLoginForm(allauthforms.LoginForm):

    password = PasswordField(label=_("Password"), autocomplete="current-password")

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(allauthforms.LoginForm, self).__init__(*args, **kwargs)
        if app_settings.AUTHENTICATION_METHOD == app_settings.AuthenticationMethod.EMAIL:
            login_widget = forms.TextInput(
                attrs={
                    "type": "email",
                    "placeholder": _("E-mail address"),
                    "autocomplete": "email",
                    "class": "form-control"
                }
            )
            login_field = forms.EmailField(label=_("E-mail"), widget=login_widget)
        elif app_settings.AUTHENTICATION_METHOD == app_settings.AuthenticationMethod.USERNAME:
            login_widget = forms.TextInput(
                attrs={"placeholder": _("Username"), "autocomplete": "username", "class": "form-control"}
            )
            login_field = forms.CharField(
                label=_("Username"),
                widget=login_widget,
                max_length=get_username_max_length(),
            )
        else:
            assert (
                app_settings.AUTHENTICATION_METHOD
                == app_settings.AuthenticationMethod.USERNAME_EMAIL
            )
            login_widget = forms.TextInput(
                attrs={"placeholder": _("Username or e-mail"), "autocomplete": "email", "class": "form-control"}
            )
            login_field = forms.CharField(
                label=pgettext("field label", "Login"), widget=login_widget
            )
        self.fields["login"] = login_field
        set_form_field_order(self, ["login", "password", "remember"])
        if app_settings.SESSION_REMEMBER is not None:
            del self.fields["remember"]

    def login(self, *args, **kwargs):

        # Add your own processing here.

        # You must return the original result.
        return super(CustomLoginForm, self).login(*args, **kwargs)

class CustomSignupForm(allauthforms.SignupForm):

    def __init__(self, *args, **kwargs):
        super(allauthforms.SignupForm, self).__init__(*args, **kwargs)
        self.fields["password1"] = PasswordField(
            label=_("Password (your account password for this site)"), autocomplete="new-password"
        )
        self.fields["email"] = fields.EmailField(label=_("E-Mail (this will be your account username)"), widget=widgets.TextInput(attrs={'type': 'email',
        'placeholder': _('E-Mail'),
        'autocomplete': 'email', 'class': 'form-control'}))
        if app_settings.SIGNUP_PASSWORD_ENTER_TWICE:
            self.fields["password2"] = PasswordField(label=_("Password (again)"))

        if hasattr(self, "field_order"):
            set_form_field_order(self, self.field_order)

    is_mailsubscribed = fields.BooleanField(label=_("Allow us to send you notifications and offers."), initial=True)

    field_order = ['email', 'email2', 'password1', 'password2', 'is_mailsubscribed']

    def save(self, request):
        # Ensure you call the parent class's save.
        # .save() returns a User object.
        user = super(CustomSignupForm, self).save(request)

        # Add your own processing here.
        user.is_mailsubscribed = self.cleaned_data['is_mailsubscribed']
        user.save()

        # You must return the original result.
        return user

class CustomSocialSignupForm(allauthsocialforms.SignupForm):

    first_name = fields.CharField(max_length=30, label=_("First Name"), 
        widget=widgets.TextInput(attrs={'placeholder': _('First name'), 'class': 'form-control'}))
    last_name = fields.CharField(max_length=30, label=_("Last Name"), 
        widget=widgets.TextInput(attrs={'placeholder': _('Last name'), 'class': 'form-control'}))
    is_mailsubscribed = fields.BooleanField(label=_("Allow us to e-mail you"), initial=True)

    field_order = ['first_name', 'last_name', 'email', 'email2', 'password1', 'password2', 'is_mailsubscribed']

    def save(self):

        # Ensure you call the parent class's save.
        # .save() returns a User object.
        user = super(CustomSocialSignupForm, self).save()

        # Add your own processing here.
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_mailsubscribed = self.cleaned_data['is_mailsubscribed']
        user.save()

        # You must return the original result.
        return user

class CustomSocialDisconnectForm(allauthsocialforms.DisconnectForm):

    def save(self):

        # Add your own processing here if you do need access to the
        # socialaccount being deleted.

        # Ensure you call the parent class's save.
        # .save() does not return anything
        super(CustomSocialDisconnectForm, self).save()

        # Add your own processing here if you don't need access to the
        # socialaccount being deleted.

class CustomAddEmailForm(allauthforms.AddEmailForm):

    email = forms.EmailField(
        label=_("E-mail"),
        required=True,
        widget=forms.TextInput(
            attrs={"type": "email", "placeholder": _("E-mail address"), "class": "form-control"}
        ),
    )


class CustomChangePasswordForm(allauthforms.ChangePasswordForm):

    oldpassword = PasswordField(
        label=_("Current Password"), autocomplete="current-password"
    )
    password1 = SetPasswordField(label=_("New Password"))
    password2 = PasswordField(label=_("New Password (again)"))

    def save(self):

        # Ensure you call the parent class's save.
        # .save() does not return anything
        super(CustomChangePasswordForm, self).save()

        # Add your own processing here.

class CustomSetPasswordForm(allauthforms.SetPasswordForm):

    password1 = SetPasswordField(label=_("Password"))
    password2 = PasswordField(label=_("Password (again)"))

    def save(self):

        # Ensure you call the parent class's save.
        # .save() does not return anything
        super(CustomSetPasswordForm, self).save()

        # Add your own processing here.

class CustomResetPasswordForm(allauthforms.ResetPasswordForm):

    email = forms.EmailField(
        label=_("E-mail"),
        required=True,
        widget=forms.TextInput(
            attrs={
                "type": "email",
                "placeholder": _("E-mail address"),
                "autocomplete": "email",
                "class": "form-control"
            }
        ),
    )

    def save(self, request):

        # Ensure you call the parent class's save.
        # .save() returns a string containing the email address supplied
        email_address = super(CustomResetPasswordForm, self).save(request)

        # Add your own processing here.

        # Ensure you return the original result
        return email_address

class CustomResetPasswordKeyForm(allauthforms.ResetPasswordKeyForm):

    password1 = SetPasswordField(label=_("Password"))
    password2 = PasswordField(label=_("Password (again)"))

    def save(self):

        # Add your own processing here.

        # Ensure you call the parent class's save.
        # .save() does not return anything
        super(CustomResetPasswordKeyForm, self).save()