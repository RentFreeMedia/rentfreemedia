import os
import uuid
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_decode
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.base import View
from django.views.generic.edit import UpdateView
from users.tokens import unsubscribe_token
from users.forms import InitialProfileMultiForm, SubsequentProfileMultiForm

UserModel = get_user_model()

def newuser_switch_view(newuser_view, olduser_view):

    @login_required
    def inner_view(request, *args, **kwargs):
        if request.user.is_newuserprofile:
            return newuser_view(request, *args, **kwargs)
        else:
            return olduser_view(request, *args, **kwargs)

    return inner_view


def upload_avatar_to(instance, filename):
    filename, ext = os.path.splitext(filename)
    return os.path.join(
        'avatar_images',
        'avatar_{uuid}_{filename}{ext}'.format(
            uuid=uuid.uuid4(), filename=filename, ext=ext)
    )


class InitialProfileView(SuccessMessageMixin, UpdateView):
    model = UserModel
    form_class = InitialProfileMultiForm
    success_message = 'Profile successfully updated'
    success_url = '/'
    template_name_suffix = '_initialprofile'

    def get_object(self):
        return get_object_or_404(UserModel, pk=self.request.user.pk)

    def get_form_kwargs(self):
        kwargs = super(InitialProfileView, self).get_form_kwargs()
        kwargs.update(instance={
            'user': self.object,
            'base_userprofile': self.object.base_userprofile,
            'wagtail_userprofile': self.object.wagtail_userprofile,
        })
        return kwargs

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        
        if self.object.is_newuserprofile:
            self.object.is_newuserprofile = False

        if form.data['user-first_name'] and form.data['user-last_name']:
            pass
        elif form.data['user-first_name']:
            pass
        else:
            self.object.first_name = form.data['user-user_name']

        self.object = form.save()
        return super().form_valid(form)

class SubsequentProfileView(SuccessMessageMixin, UpdateView):
    model = UserModel
    form_class = SubsequentProfileMultiForm
    success_message = 'Profile successfully updated'
    success_url = '/'
    template_name_suffix = '_subsequentprofile'

    def get_object(self):
        return get_object_or_404(UserModel, pk=self.request.user.pk)

    def get_form_kwargs(self):
        kwargs = super(SubsequentProfileView, self).get_form_kwargs()
        kwargs.update(instance={
            'user': self.object,
            'base_userprofile': self.object.base_userprofile,
            'wagtail_userprofile': self.object.wagtail_userprofile,
        })
        return kwargs

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        
        if form.data['user-first_name'] and form.data['user-last_name']:
            pass
        elif form.data['user-first_name']:
            pass
        else:
            self.object.first_name = form.data['user-user_name']

        self.object = form.save()
        return super().form_valid(form)


class UnsubscribeView(View):
    def get(self, request, *args, **kwargs):
        try:
            user = UserModel.objects.get(email=urlsafe_base64_decode(kwargs['uidb64']).decode())
            token = kwargs['token']
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist, ValidationError):
            user = None
        if user and unsubscribe_token.check_token(user, token):
            user.is_mailsubscribed = False
            user.save()
            return render(request, 'account/unsubscribe.html')
        else:
            return render(request, 'account/invalid.html')
