import mimetypes
import os
from datetime import datetime
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, HttpResponsePermanentRedirect, HttpResponseForbidden
from django.shortcuts import render
from django.utils.http import urlsafe_base64_decode
from django.views.generic.base import View
from users.tokens import premium_token
from urllib.parse import urlparse
from users.models import CustomUserProfile
from wagtail.contrib.forms.views import SubmissionsListView as WagtailSubmissionsListView
from wagtail.core.models import Site
from website.models.choices import page_choices
from website.models.media import CustomMedia, Download
from website.models.settings import LayoutSettings
from website.utils import attempt_protected_media_value_conversion

UserModel = get_user_model()


def favicon(request):
    site = Site.find_for_request(request)
    icon = LayoutSettings.for_site(site).favicon
    if icon:
        return HttpResponsePermanentRedirect(icon.get_rendition('original').url)
    raise Http404()


def robots(request):
    return render(
        request,
        'robots.txt',
        content_type='text/plain'
    )


class SubmissionsListView(WagtailSubmissionsListView):

    def get_csv_response(self, context):
        filename = self.get_csv_filename()
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment;filename={}'.format(filename)

        writer = csv.writer(response)
        writer.writerow(context['data_headings'])
        for data_row in context['data_rows']:
            modified_data_row = []
            for cell in data_row:
                modified_cell = attempt_protected_media_value_conversion(self.request, cell)
                modified_data_row.append(modified_cell)

            writer.writerow(modified_data_row)
        return response


class PremiumMediaView(View):
    def get(self, request, uidb64, fileid, token, file_name):
        try:
            user = UserModel.objects.get(email=urlsafe_base64_decode(uidb64).decode())
        except:
            user = None
        try:
            file = CustomMedia.objects.get(pk=fileid)
        except:
            raise Http404('No such file exists')
        if user and premium_token.check_token(user, token) and user.stripe_subscription.status == 'active':
            url = file.url
            protocol = urlparse(url).scheme
            userprofile = CustomUserProfile.objects.get(user_id=user.id)
            userprofile.media_download.add(file)
            download_record = Download.objects.filter(user_id=user.id).filter(media_id=fileid).first()
            download_record.download_count += 1
            download_record.last = datetime.now()
            download_record.save()
            response = HttpResponse()
            response['X-Accel-Redirect'] = '/media_download/' + protocol + '/' + url.replace(protocol + '://', '')
            return response
        else:
            return HttpResponseForbidden()

