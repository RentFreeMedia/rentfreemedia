import string
import random
import re
import os
import pathlib

from django import template
from django.conf import settings
from django.forms import ClearableFileInput

from django.utils.html import mark_safe, strip_tags
from django.utils.http import urlsafe_base64_encode
from pytube import extract
from videos_id.video_info import VideoInfo
from wagtail.core.models import Collection
from wagtail.core.templatetags.wagtailcore_tags import richtext

from wagtail.images.models import Image
from website import __version__
from website.forms import SearchForm
from website.utils import uri_validator, get_protected_media_link, uri_validator
from website.models.choices import get_bootstrap_setting, page_choices


register = template.Library()

@register.filter
def base64(value):
    return urlsafe_base64_encode(value.encode())

@register.filter
def isoduration(value):
    return int(value)//60

@register.filter
def stripslash(value):
    return value.replace('/','')


@register.simple_tag
def website_version():
    return __version__


@register.simple_tag
def generate_random_id():
    return ''.join(random.choice(string.ascii_letters + string.digits) for n in range(20))

@register.filter
def is_file_form(form):
    return any([isinstance(field.field.widget, ClearableFileInput) for field in form])

@register.simple_tag(takes_context=True)
def og_image(context, page):

    protocol = re.compile(r'^(\w[\w\.\-\+]*:)*//')

    if protocol.match(settings.MEDIA_URL):
        base_url = ''
    else:
        base_url = context['settings'].request_or_site.root_url

    if page:
        if page.og_image:
            return base_url + page.og_image.get_rendition('original').url
        elif page.cover_image:
            return base_url + page.cover_image.get_rendition('original').url
    site = context['settings'].request_or_site
    if site.layoutsettings.logo:
        return site.layoutsettings.logo.get_rendition('original').url
    return None

@register.simple_tag
def get_pictures(collection_id):
    collection = Collection.objects.get(id=collection_id)
    return Image.objects.filter(collection=collection)


@register.simple_tag
def get_searchform(request=None):
    if request:
        return SearchForm(request.GET)
    return SearchForm()

@register.simple_tag(takes_context=True)
def snippet_footer(context):

    account_urlnames = [
        'account',
        'account_email',
        'account_email_verification_sent',
        'account_change_password',
        'account_login',
        'account_logout',
        'account_reset_password',
        'account_signup',
        'profile',
        'two-factor-setup',
        'two-factor-backup-tokens',
        'two-factor-authenticate',
        'two-factor-remove'
    ]
    site = context['settings'].request_or_site
    if context['request'].resolver_match.url_name in account_urlnames:        
        try:
            page_footer = site.layoutsettings.account_footer
        except:
            page_footer = None
    elif 'subscribe' in context['request'].resolver_match.url_name:
        try:
            page_footer = site.layoutsettings.subscribe_footer
        except:
            page_footer = None
    elif 'search' in context['request'].resolver_match.url_name:
        try:
            page_footer = site.layoutsettings.search_footer
        except:
            page_footer = None
    else:
        page_footer = None

    if page_footer:
        if page_footer.custom_css_class and page_footer.custom_id:
            pre_footer = '<div class=' + '"' + page_footer.custom_css_class + '"' + ' id=' + '"' + page_footer.custom_id + '"' + '>\n'
            post_footer = '</div>\n'
        elif page_footer.custom_css_class: 
            pre_footer = '<div class=' + '"' + page_footer.custom_css_class + '"' + '>\n'
            post_footer = '</div>\n'
        elif page_footer.custom_id:
            pre_footer = '<div id=' + '"' + page_footer.custom_id + '"' + '>\n'
            post_footer = '</div>\n'
        else:
            pre_footer = '<div>\n'
            post_footer = '</div>\n'
        return mark_safe(pre_footer + page_footer.content.render_as_block() + post_footer)
    else:
        return ''

@register.simple_tag(takes_context=True)
def snippet_header(context):

    account_urlnames = [
        'account',
        'account_email',
        'account_email_verification_sent',
        'account_change_password',
        'account_login',
        'account_logout',
        'account_reset_password',
        'account_signup',
        'profile',
        'two-factor-setup',
        'two-factor-backup-tokens',
        'two-factor-authenticate',
        'two-factor-remove'
    ]
    site = context['settings'].request_or_site
    if context['request'].resolver_match.url_name in account_urlnames:
        try:
            page_header = site.layoutsettings.account_header
        except:
            page_header = None
    elif 'subscribe' in context['request'].resolver_match.url_name:
        try:
            page_header = site.layoutsettings.subscribe_header
        except:
            page_header = None
    elif 'search' in context['request'].resolver_match.url_name:
        try:
            page_header = site.layoutsettings.search_header
        except:
            page_header = None
    else:
        page_header = None

    if page_header:
        if page_header.custom_css_class and page_header.custom_id:
            pre_header = '<div class=' + '"' + page_header.custom_css_class + '"' + ' id=' + '"' + page_header.custom_id + '"' + '>\n'
            post_header = '</div>\n'
        elif page_header.custom_css_class: 
            pre_header = '<div class=' + '"' + page_header.custom_css_class + '"' + '>\n'
            post_header = '</div>\n'
        elif page_header.custom_id:
            pre_header = '<div id=' + '"' + page_header.custom_id + '"' + '>\n'
            post_header = '</div>\n'
        else:
            pre_header = '<div>\n'
            post_header = '</div>\n'
        return mark_safe(pre_header + page_header.content.render_as_block() + post_header)
    else:
        return ''

@register.simple_tag
def process_form_cell(request, cell):
    if isinstance(cell, str) and cell.startswith(page_choices['PROTECTED_MEDIA_URL']):
        return get_protected_media_link(request, cell, render_link=True)
    if uri_validator(str(cell)):
        return mark_safe("<a href='{0}'>{1}</a>".format(cell, cell))
    return cell

@register.simple_tag
def get_pageform(page, request):
    return page.get_form(request)

@register.filter
def django_settings(value):
    return getattr(settings, value)

@register.simple_tag
def query_update(querydict, key=None, value=None):

    get = querydict.copy()
    if key:
        if value:
            get[key] = value
        else:
            try:
                del(get[key])
            except KeyError:
                pass
    return get


@register.simple_tag(takes_context=True)
def basefilename(context):
    
    filename = os.path.basename(context.template_name).split('.')[0].replace(r'_',' ').title()
    return filename

@register.filter
def bootstrap_settings(value):
    return get_bootstrap_setting(value)

@register.filter
def extension(value):
    extension = pathlib.Path(value).suffix.split('.')[-1]
    if extension:
        return extension
    else:
        return None

@register.filter
def get_fields(obj):
    return [(field.name, field.value_to_string(obj)) for field in obj._meta.fields]

@register.filter
def map_to_bootstrap_alert(message_tag):
    """
    Converts a message level to a bootstrap 4 alert class
    """
    message_to_alert_dict = {
        'debug': 'primary',
        'info': 'info',
        'success': 'success',
        'warning': 'warning',
        'error': 'danger'
    }

    try:
        return message_to_alert_dict[message_tag]
    except KeyError:
        return ''

@register.filter
def titlesplit(value):
    title = value.split(' (')[0].replace(r'-',' ').replace(r'_',' ')
    if title:
        return title
    else:
        return None

@register.filter
def icon_name(value):
    if ' ' in value:
        return value.split(' ', 1)[0]
    else:
        return value


@register.simple_tag
def relative_url(value, field_name, urlencode=None):
    url = '?{}={}'.format(field_name, value)
    if urlencode:
        querystring = urlencode.split('&')
        filtered_querystring = filter(lambda p: p.split('=')[0] != field_name, querystring)
        encoded_querystring = '&'.join(filtered_querystring)
        url = '{}&{}'.format(url, encoded_querystring)
    return url

@register.filter
def youtubeid(value):
    id = extract.video_id(value)
    if id:
        return id
    else:
        return None

@register.filter
def vimeoid(value):
    video_info = VideoInfo()
    id = video_info.check_video_id(value)
    if id:
        return id
    else:
        return None

@register.filter
def strip_markup(value):
    if value:
        text = value.replace('>', '> ')
        new_value = strip_tags(text)
    else:
        new_value = value
    return new_value

