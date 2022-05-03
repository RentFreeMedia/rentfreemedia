import bleach
import json
import logging
import lxml
import os
import pathlib
import requests
import uuid
from comment.models import Comment
from datetime import datetime
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.core.files.storage import FileSystemStorage
from django.core.mail import EmailMessage
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models import Q
from django.db.models.expressions import F
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template import Context, Template
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_decode
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import cache_control
from django_summernote.widgets import SummernoteWidget
from modelcluster.fields import ParentalKey
from modelcluster.models import get_all_child_relations
from modelcluster.tags import ClusterTaggableManager
from pathlib import Path
from post_office import mail
from taggit.models import TaggedItemBase
from users.tokens import premium_token
from wagtail.admin.edit_handlers import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    PageChooserPanel,
    StreamFieldPanel,
    TabbedInterface
)
from wagtailmedia.edit_handlers import MediaChooserPanel
from wagtail.core import hooks
from wagtail.core.fields import StreamField
from wagtail.core.models import Orderable, PageBase, Page, PageLogEntry, Site, TranslatableMixin, _copy, _copy_m2m_relations
from wagtail.core.utils import resolve_model_string
from wagtail.core.signals import page_published
from wagtail.contrib.forms.edit_handlers import FormSubmissionsPanel
from wagtail.contrib.forms.forms import WagtailAdminFormPageForm
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.contrib.forms.forms import FormBuilder as WagtailFormBuilder
from wagtail.contrib.forms.models import FormSubmission
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.utils.decorators import cached_classmethod
from wagtailcache.cache import cache_page, nocache_page, WagtailCacheMixin
from wagtail_personalisation.models import PersonalisablePageMixin, PersonalisablePageMetadata
from wagtail_personalisation.utils import exclude_variants
from website import utils
from website.forms import (
    DateTimeField,
    DateField,
    TimeField
)
from website.models.blocks import (
    layout_streamblocks,
    streamform_blocks,
    contentpage_streamblocks,
    ContentWallBlock
)
from website.models.choices import page_choices
from website.models.rules import TierEqualOrGreater, TierEqual
from website.models.settings import GeneralSettings, LayoutSettings, SeoSettings
from website.models.snippets import Email
from website.article_feeds import ArticleFeed
from website.podcast_feeds import PodcastFeed
from website.views import SubmissionsListView
from website.wagtail_flexible_forms.blocks import FormFieldBlock, FormStepBlock
from website.wagtail_flexible_forms.models import (
    Step,
    Steps,
    StreamFormMixin as FlexibleformStreamFormMixin,
    StreamFormJSONEncoder,
    SessionFormSubmission as FlexibleformSessionFormSubmission,
    SubmissionRevision as FlexibleformSubmissionRevision
)

from bs4 import BeautifulSoup

logger = logging.getLogger('website')


WEB_PAGE_MODELS = []

UserModel = get_user_model()


def get_page_models():
    return WEB_PAGE_MODELS


class BasePageMeta(PageBase):
    def __init__(cls, name, bases, dct):
        super().__init__(name, bases, dct)
        if 'search_db_include' not in dct:
            cls.search_db_include = False
        if 'search_db_boost' not in dct:
            cls.search_db_boost = 0
        if 'search_filterable' not in dct:
            cls.search_filterable = False
        if 'search_name' not in dct:
            cls.search_name = cls._meta.verbose_name
        if 'search_name_plural' not in dct:
            cls.search_name_plural = cls._meta.verbose_name_plural
        if 'search_template' not in dct:
            cls.search_template = 'search/search_result.html'
        if not cls._meta.abstract:
            WEB_PAGE_MODELS.append(cls)


class PageTag(TaggedItemBase):
    class Meta:
        verbose_name = _('Page Tag')
    content_object = ParentalKey('website.BasePage', related_name='tagged_items')


class BasePage(Page, metaclass=BasePageMeta):

    class Meta:
        verbose_name = _('Website Page')

    is_creatable = False

    ###############
    # Content fields
    ###############

    cover_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_('Cover image'),
    )

    ###############
    # Index fields
    ###############

    index_show_subpages_default = False

    index_query_pagemodel = 'website.BasePage'

    index_order_by_default = '-first_published_at'
    index_order_by_choices = (
        ('-first_published_at', _('Date first published, newest to oldest')),
        ('first_published_at', _('Date first published, oldest to newest')),
        ('-last_published_at', _('Date updated, newest to oldest')),
        ('last_published_at', _('Date updated, oldest to newest')),
        ('title', _('Title, alphabetical')),
        ('-title', _('Title, reverse alphabetical')),
    )
    index_show_subpages = models.BooleanField(
        default=index_show_subpages_default,
        verbose_name=_('Show list of child pages')
    )
    index_order_by = models.CharField(
        max_length=255,
        choices=index_order_by_choices,
        default=index_order_by_default,
        blank=True,
        verbose_name=_('Order child pages by'),
    )
    index_num_per_page = models.PositiveIntegerField(
        default=10,
        verbose_name=_('Number per page'),
    )
    
    ###############
    # Layout fields
    ###############

    custom_template = models.CharField(
        blank=True,
        max_length=255,
        choices=None,
        verbose_name=_('Template')
    )

    page_header = models.ForeignKey(
        'website.Header',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_('Header/Navbar'),
        help_text=_('Header / navbar for this page.'),
    )

    page_footer = models.ForeignKey(
        'website.Footer',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_('Footer'),
        help_text=_('Footer for this page.'),
    )

    ###############
    # SEO fields
    ###############

    og_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_('Open Graph preview image'),
        help_text=_("The image shown when linking to this page on social media. If blank, defaults to page cover image, or logo in Settings > Layout > Logo"),  # noqa
    )

    ###############
    # Tags
    ###############

    tags = ClusterTaggableManager(
        through=PageTag,
        blank=True,
        verbose_name=_('Tags'),
        help_text=_('Used to organize pages across the site.'),
    )

    ###############
    # Settings
    ###############

    content_walls = StreamField(
        [
            ('content_wall', ContentWallBlock())
        ],
        blank=True,
        verbose_name=_('Content Walls')
    )

    ###############
    # Search
    ###############

    search_fields = [
        index.SearchField('title', partial_match=True, boost=3),
        index.SearchField('seo_title', partial_match=True, boost=3),
        index.SearchField('search_description', boost=2),
        index.FilterField('title'),
        index.FilterField('id'),
        index.FilterField('live'),
        index.FilterField('owner'),
        index.FilterField('content_type'),
        index.FilterField('path'),
        index.FilterField('depth'),
        index.FilterField('locked'),
        index.FilterField('first_published_at'),
        index.FilterField('last_published_at'),
        index.FilterField('latest_revision_created_at'),
        index.FilterField('index_show_subpages'),
        index.FilterField('index_order_by'),
        index.FilterField('custom_template'),
    ]

    ###############
    # Panels
    ###############

    content_panels = Page.content_panels + [
        ImageChooserPanel('cover_image'),
    ]

    body_content_panels = []

    bottom_content_panels = []

    tags_panels = [
        FieldPanel('tags'),
    ]

    layout_panels = [
        MultiFieldPanel(
            [
                FieldPanel('custom_template'),
                SnippetChooserPanel('page_header'),
                SnippetChooserPanel('page_footer'),
            ],
            heading=_('Visual Design'),
            classname='collapsible'
        )
    ]

    promote_panels = [
        MultiFieldPanel(
            [
                FieldPanel('slug'),
                FieldPanel('seo_title'),
                FieldPanel('search_description'),
                ImageChooserPanel('og_image'),
            ],
            _('Page Meta Data'),
            classname='collapsible'
        ),
    ]

    settings_panels = Page.settings_panels + [
        StreamFieldPanel('content_walls'),
    ]

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        klassname = self.__class__.__name__.lower()
        template_choices = page_choices['TEMPLATES_PAGES'].get('*', ()) + \
            page_choices['TEMPLATES_PAGES'].get(klassname, ())

        self._meta.get_field('index_order_by').choices = self.index_order_by_choices
        self._meta.get_field('custom_template').choices = template_choices
        if not self.id:
            self.index_order_by = self.index_order_by_default
            self.index_show_subpages = self.index_show_subpages_default

    @cached_classmethod
    def get_edit_handler(cls):

        panels = [
            ObjectList(
                cls.content_panels + cls.body_content_panels + cls.bottom_content_panels,
                heading=_('Content')
            ),
            ObjectList(cls.tags_panels, heading=_('Tags')),
            ObjectList(cls.layout_panels, heading=_('Layout')),
            ObjectList(cls.promote_panels, heading=_('SEO'), classname="seo"),
            ObjectList(cls.settings_panels, heading=_('Settings'), classname="settings"),
        ]

        return TabbedInterface(panels).bind_to(model=cls)

    def get_struct_org_type(context):

        try:
            seo_settings = Site.find_for_request(context['request']).SeoSettings
        except:
            seo_settings = None
        if seo_settings:
            if seo_settings.struct_org_type:
                return True
            else:
                return False
        else:
            return False

    def get_struct_org_name(context):

        try:
            seo_settings = Site.find_for_request(context['request']).SeoSettings
        except:
            seo_settings = None
        if seo_settings.struct_org_name:
            return seo_settings.struct_org_name
        return self.get_site().site_name

    def get_struct_org_logo(context):

        try:
            seo_settings = Site.find_for_request(context['request']).SeoSettings
        except:
            seo_settings = None
        if seo_settings.struct_org_logo:
            return seo_settings.struct_org_logo
        else:
            try:
                layout_settings = Site.find_for_request(context['request']).LayoutSettings
            except:
                layout_settings = None
            if layout_settings.logo:
                return layout_settings.logo
        return None

    def get_template(self, request, *args, **kwargs):

        if self.custom_template:
            return self.custom_template

        return super(BasePage, self).get_template(request, args, kwargs)

    def get_index_children(self):
        """
        Returns query of subpages as defined by `index_` variables.
        """
        if self.index_query_pagemodel:
            querymodel = resolve_model_string(self.index_query_pagemodel, self._meta.app_label)
            query = exclude_variants(querymodel.objects.child_of(self).live())
        else:
            query = exclude_variants(self.get_children().live())

        # Determine query sorting order.
        order = []

        # Order by the specified model attribute if specified.
        if self.index_order_by:
            order.append(self.index_order_by)

        # Order the query.
        if order:
            query = query.order_by(*order)

        return query

    def is_canonical_page(self):
        try:
            canonical_page = self.specific.personalisation_metadata.is_canonical
        except:
            return True
        return canonical_page

    def get_content_walls(self):
        try:
            return self.content_walls
        except:
            return None

    def is_podcast_index(self):

        return False

    def is_article_index(self):

        return False

    def get_context(self, request, *args, **kwargs):

        context = super().get_context(request)

        if self.index_show_subpages:
            all_children = self.get_index_children()
            paginator = Paginator(all_children, self.index_num_per_page)
            pagenum = request.GET.get('p', 1)
            try:
                paged_children = paginator.page(pagenum)
            except (PageNotAnInteger, EmptyPage, InvalidPage) as e:
                paged_children = paginator.page(1)

            context['index_paginated'] = paged_children
            context['index_children'] = all_children
        context['content_walls'] = self.get_content_walls()
        return context

    def has_form_include(self):

        if self.body.raw_data:
            if ('pagepreview_block_form.html' or 'render_field.html') in self.body.raw_data.__repr__():
                return True
            else:
                return False
        else:
            return False


class WebPage(BasePage):
    """
    Provides a body and body-related functionality.
    This is abstract so that subclasses can override the body StreamField.
    """
    class Meta:
        verbose_name = _('Web Page')
        abstract = True

    comments = GenericRelation(Comment)

    template = 'website/pages/web_page.html'

    # Child pages should override based on what blocks they want in the body.
    # Default is LAYOUT_STREAMBLOCKS which is the fullest editor experience.
    body = StreamField(layout_streamblocks, null=True, blank=True)

    # Search fields
    search_fields = (
        BasePage.search_fields +
        [index.SearchField('body')]
    )

    # Panels
    body_content_panels = [
        StreamFieldPanel('body'),
    ]

    @property
    def body_preview(self):
        """
        A shortened version of the body without HTML tags.
        """
        item_bodytext = self.body.render_as_block()
        soup = BeautifulSoup(item_bodytext, 'lxml')
        preview_clean = bleach.clean(str(soup.select_one('.block-body_text'))[:400], strip=True, tags=['p', 'a'])
        return strip_tags(preview_clean.replace('>', '> ')) + '...'

    @property
    def page_ptr(self):
        """
        Overwrite of `page_ptr` to make it compatible with wagtailimportexport.
        """
        return self.base_page_ptr

    @page_ptr.setter
    def page_ptr(self, value):
        self.base_page_ptr = value

    @property
    def get_page_title(self):

        if self.seo_title:
            title = self.seo_title
        elif self.title:
            title = self.title.split(' (')[0]
        elif self.url:
            title = self.url.strip('/').replace(r'-',' ').title()
        else:
            title = os.path.basename(self.template_name).split('.')[0].replace(r'_',' ').title()
        return title

    @property
    def can_have_comments(self):
        pages = ['PodcastContentPage', 'ArticleContentPage']
        if self.__class__.__name__ in pages:
            return True
        else:
            return False


class PodcastPageAuthor(Orderable, index.Indexed):
    page = ParentalKey('website.PodcastContentPage', on_delete=models.CASCADE, related_name='author')

    def get_author_list():
        g = Group.objects.get(name='Authors')
        return {'groups__in': [g, ]}

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to=get_author_list,
        null=True,
        blank=True,
        editable=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Author'),
    )

    author_display = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Display as'),
        help_text=_('Override how the author’s name displays on this page.'),
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel('author', help_text='Author / Host / Creator'),
                FieldPanel('author_display')
            ],
            _('Author/Creator/Host')
        )
    ]

    search_fields = [
        index.RelatedFields('author', [
                index.SearchField('first_name'),
                index.SearchField('last_name'),
            ])
    ]

    @property
    def first_name(self):
        if self.author.first_name:
            return self.author.first_name
        else:
            return None

    @property
    def last_name(self):
        if self.author.last_name:
            return self.author.last_name
        else:
            return None

    @property
    def user_name(self):
        if self.author.user_name:
            return self.author.user_name
        else:
            return None

    @property
    def url(self):
        if self.author.url:
            return self.author.url
        else:
            return None

    @property
    def user_object(self):
        profile_id = self.author_id
        user_obj = UserModel.objects.get(pk=profile_id)
        return user_obj


class PodcastPageContributor(Orderable, index.Indexed):
    page = ParentalKey('website.PodcastContentPage', on_delete=models.CASCADE, related_name='contributor')

    def get_contributor_list():
        g = Group.objects.get(name='Contributors')
        return {'groups__in': [g, ]}

    contributor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to=get_contributor_list,
        null=True,
        blank=True,
        editable=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Contributor')
    )

    contributor_display = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Display as'),
        help_text=_('Override how the contributor’s name displays on this page.'),
    )

    contributor_url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('External link'),
        help_text=_('Optionally wrap "Display as" name in a link.'),
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel('contributor', help_text='Contributor or guest'),
                FieldPanel('contributor_display'),
                FieldPanel('contributor_url'),
            ],
            _('Contributor')
        )
    ]

    @property
    def first_name(self):
        if self.contributor.first_name:
            return self.contributor.first_name
        else:
            return None

    @property
    def last_name(self):
        if self.contributor.last_name:
            return self.contributor.last_name
        else:
            return None

    @property
    def user_name(self):
        if self.contributor.user_name:
            return self.contributor.user_name
        else:
            return None

    @property
    def user_object(self):
        profile_id = self.contributor_id
        user_obj = UserModel.objects.get(pk=profile_id)
        return user_obj


class ArticlePageAuthor(Orderable, index.Indexed):
    page = ParentalKey('website.ArticleContentPage', on_delete=models.CASCADE, related_name='author')

    def get_author_list():
        g = Group.objects.get(name='Authors')
        return {'groups__in': [g, ]}

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to=get_author_list,
        null=True,
        blank=True,
        editable=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Author'),
    )

    author_display = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Display as'),
        help_text=_('Override how the author’s name displays on this page.'),
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel('author', help_text='Author / Host / Creator'),
                FieldPanel('author_display')
            ],
            _('Author/Creator/Host')
        )
    ]

    search_fields = [
        index.RelatedFields('author', [
                index.SearchField('first_name'),
                index.SearchField('last_name'),
            ])
    ]

    @property
    def first_name(self):
        if self.author.first_name:
            return self.author.first_name
        else:
            return None

    @property
    def last_name(self):
        if self.author.last_name:
            return self.author.last_name
        else:
            return None

    @property
    def user_name(self):
        if self.author.user_name:
            return self.author.user_name
        else:
            return None

    @property
    def url(self):
        if self.author.url:
            return self.author.url
        else:
            return None

    @property
    def user_object(self):
        profile_id = self.author_id
        user_obj = UserModel.objects.get(pk=profile_id)
        return user_obj


class ArticlePageContributor(Orderable, index.Indexed):
    page = ParentalKey('website.ArticleContentPage', on_delete=models.CASCADE, related_name='contributor')

    def get_contributor_list():
        g = Group.objects.get(name='Contributors')
        return {'groups__in': [g, ]}

    contributor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to=get_contributor_list,
        null=True,
        blank=True,
        editable=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Contributor')
    )

    contributor_display = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Display as'),
        help_text=_('Override how the contributor’s name displays on this page.'),
    )

    contributor_url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('External url'),
        help_text=_('Optionally wrap "Display as" name in a link.'),
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel('contributor', help_text='Contributor or guest'),
                FieldPanel('contributor_display'),
                FieldPanel('contributor_url'),
            ],
            _('Contributor')
        )
    ]

    @property
    def first_name(self):
        if self.contributor.first_name:
            return self.contributor.first_name
        else:
            return None

    @property
    def last_name(self):
        if self.contributor.last_name:
            return self.contributor.last_name
        else:
            return None

    @property
    def user_name(self):
        if self.contributor.user_name:
            return self.contributor.user_name
        else:
            return None

    @property
    def user_object(self):
        profile_id = self.contributor_id
        user_obj = UserModel.objects.get(pk=profile_id)
        return user_obj

class GenericPage(WagtailCacheMixin, PersonalisablePageMixin, WebPage):
    """
    General use page with featureful streamfield and SEO attributes.
    """
    struct_org_json = models.TextField(
        blank=True,
        verbose_name=_('Schema data'),
        help_text=_('Since this page is freeform so is the metadata: add a COMPLETE json+ld section here (WITHOUT <script> tags) if you wish.'),  # noqa
    )

    class Meta:
        verbose_name = 'Generic Page'

    template = 'website/pages/web_page.html'

    body = StreamField(layout_streamblocks, null=True, blank=True)

    # Search fields
    search_fields = (
        WebPage.search_fields +
        [index.SearchField('body')]
    )

    # Panels
    body_content_panels = [
        StreamFieldPanel('body'),
    ]

    promote_panels = [
        MultiFieldPanel(
            [
                FieldPanel('slug'),
                FieldPanel('seo_title'),
                FieldPanel('search_description'),
                ImageChooserPanel('og_image'),
                FieldPanel('struct_org_json'),
            ],
            _('Page Meta Data'),
            classname='collapsible'
        ),
    ]

    @property
    def body_preview(self):
        """
        A shortened version of the body without HTML tags.
        """
        item_bodytext = self.body.render_as_block()
        soup = BeautifulSoup(item_bodytext, 'lxml')
        preview_clean = bleach.clean(str(soup.select_one('.block-body_text'))[:400], strip=True, tags=['p', 'a'])
        return mark_safe(preview_clean) + '...'

    @property
    def page_ptr(self):
        """
        Overwrite of `page_ptr` to make it compatible with wagtailimportexport.
        """
        return self.base_page_ptr

    @page_ptr.setter
    def page_ptr(self, value):
        self.base_page_ptr = value


class PodcastContentIndexPage(WagtailCacheMixin, RoutablePageMixin, WebPage):
    """
    Shows a list of content sub-pages.
    """
    def get_author_list():
        g = Group.objects.get(name='Authors')
        return {'groups__in': [g, ]}

    class Meta:
        verbose_name = _('Index Page for a Podcast')
        abstract = False

    index_show_subpages_default = True

    index_query_pagemodel = 'website.PodcastContentPage'

    index_order_by_default = '-date_display'
    index_order_by_choices = (('-date_display', 'Display publish date, newest first'),) + \
        WebPage.index_order_by_choices

    parent_page_types = ['website.GenericPage']

    subpage_types = ['website.PodcastContentPage']

    template = 'website/pages/content_index_page.html'

    show_images = models.BooleanField(
        default=True,
        verbose_name=_('Show images'),
    )
    show_captions = models.BooleanField(
        default=True,
    )
    show_meta = models.BooleanField(
        default=True,
        verbose_name=_('Show author and date info'),
    )
    show_preview_text = models.BooleanField(
        default=True,
        verbose_name=_('Show preview text'),
    )

    rss_main_entity = models.BooleanField(
        choices=page_choices['BOOLEAN_CHOICES'],
        verbose_name=_('Main entity of the site?'),
        help_text=_('Works with site settings SEO data: is this the primary media production of this site?'),
        db_index=True
    )

    rss_ttl = models.CharField(
        max_length=10,
        verbose_name=_('RSS TTL'),
        help_text=_('The RSS channel time to live (cache), or estimated time between episodes (minutes). Valid entries: HH:MM and MM.')
    )

    rss_title = models.CharField(
        verbose_name=_('RSS Title'),
        max_length=255,
        help_text=_('The RSS channel title (required).')
    )

    rss_itunes_title = models.CharField(
        blank=True,
        null=True,
        verbose_name=_('iTunes title'),
        max_length=50,
        help_text=_('An RSS channel title specific to iTunes/Apple Podcasts.')
    )

    rss_description = models.TextField(
        null=False,
        blank=False,
        default=' ',
        verbose_name=_('RSS Description'),
        help_text=_('The RSS channel description (required). Basic HTML enabled.')
    )

    rss_itunes_description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('RSS Description'),
        help_text=_('The RSS channel description if you want plain text, if filled this will be the default in place of the HTML description above.')
    )

    rss_itunes_primary_category = models.CharField(
        choices=page_choices['RSS_ITUNES_CATEGORY_CHOICES'],
        max_length=50,
        verbose_name=_('iTunes category #1'),
        help_text=_('The iTunes primary content category for the show in this index. See: https://help.apple.com/itc/podcasts_connect/#/')
    )

    rss_itunes_primary_subcategory = models.CharField(
        blank=True,
        null=True,
        max_length=50,
        choices=page_choices['RSS_ITUNES_SUBCATEGORY_CHOICES'],
        verbose_name=_('iTunes subcategory #1'),
        help_text=_('Optional, the iTunes subcategory beneath your main one. Not all categories have subcategories, only choose a relevant option beneath your main category.'),
    )

    rss_itunes_secondary_category = models.CharField(
        blank=True,
        null=True,
        choices=page_choices['RSS_ITUNES_CATEGORY_CHOICES'],
        max_length=50,
        verbose_name=_('iTunes category #2'),
        help_text=_('The second iTunes primary content category for the show in this index. See: https://help.apple.com/itc/podcasts_connect/#/')
    )

    rss_itunes_secondary_subcategory = models.CharField(
        blank=True,
        null=True,
        choices=page_choices['RSS_ITUNES_SUBCATEGORY_CHOICES'],
        max_length=50,
        verbose_name=_('iTunes subcategory #2'),
        help_text=_('Optional, the second iTunes subcategory beneath your main one. Not all categories have subcategories, only choose a relevant option beneath your main category.'),
    )

    rss_google_category = models.CharField(
        blank=True,
        null=True,
        max_length=50,
        choices=page_choices['RSS_GOOGLE_CATEGORY_CHOICES'],
        verbose_name=_('Google category'),
        help_text=_('Google has slightly different categories than Apple, if your iTunes category does not exist on Google, you can select a Google category option here.'),
    )

    rss_preview_text = models.CharField(
        blank=True,
        null=True,
        max_length=50,
        verbose_name=_('Preview prefix'),
        help_text=_('Freeform. This will be prepended to episodes flagged as previews of paid content if you include previews in your feed. Ex: "PREVIEW--"')
    )

    rss_omit_previews = models.BooleanField(
        choices=page_choices['BOOLEAN_CHOICES'],
        verbose_name=_('Omit previews'),
        help_text=_('Should preview episodes be omitted from your RSS feed? They will still appear on the website index page. This should probably be used in conjunction with the option to omit episode numbers from your RSS feed.')
    )

    rss_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_('RSS image'),
        help_text=_('iTunes RSS channel logo image, per Apple: 1400px x 1400px to 3000px x 3000px, square PNG or JPEG.')
    )

    rss_premium_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_('RSS premium image'),
        help_text=_('The RSS image which will appear for premium feed users on the paid tier(s)')
    )

    rss_itunes_explicit = models.BooleanField(
        choices=page_choices['BOOLEAN_CHOICES'],
        verbose_name=_('iTunes explicit'),
        help_text=_('Explicit language flag at the channel level, and the default for episodes under this index.')
    )

    rss_combine_private = models.BooleanField(
        choices=page_choices['BOOLEAN_CHOICES'],
        verbose_name=_('Combine Feeds'),
        help_text=_('Combine private and public feed for subscribers, so that they can unfollow/unsubscribe the public feed.')
    )

    rss_include_episode_number = models.BooleanField(
        choices=page_choices['BOOLEAN_CHOICES'],
        verbose_name=_('Episode numbers'),
        help_text=_('Include episode numbers in the RSS feed?')
    )

    rss_itunes_type = models.CharField(
        choices=page_choices['RSS_ITUNES_TYPE_CHOICES'],
        max_length=15,
        verbose_name=_('iTunes type'),
        help_text=_('iTunes espisode listing type. Serial for oldest first, episodic for newest first.')
    )

    rss_itunes_author = models.CharField(
        blank=True,
        null=True,
        max_length=150,
        verbose_name=_('iTunes author'),
        help_text=_('Optional, will set the iTunes author or (comma separated) authors, or defaults to the feed title if this is left blank.')
    )

    rss_itunes_owner = models.CharField(
        blank=True,
        null=True,
        max_length=25,
        verbose_name=_('iTunes owner'),
        help_text=_('Optional, admin contact, will set the iTunes owner, which otherwise defaults to the feed title.')
    )

    rss_itunes_owner_email = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        limit_choices_to=get_author_list,
        on_delete=models.SET_NULL,
        verbose_name=_('iTunes email'),
        help_text=_('Optional, admin contact, will set the iTunes owner email, which otherwise defaults to the Django admin email. Note: email will be published.')
    )

    rss_itunes_copyright = models.CharField(
        blank=True,
        null=True,
        max_length=75,
        verbose_name=_('iTunes copyright'),
        help_text=_('Optional, custom iTunes copyright name / organization. If omitted, will default to the feed title. DO NOT PUT DATES, they are auto-calculated.')
    )

    layout_panels = WebPage.layout_panels + [
        MultiFieldPanel(
            [
                FieldPanel('index_show_subpages'),
                FieldPanel('index_num_per_page'),
                FieldPanel('index_order_by'),
            ],
            heading=_('Show Child Pages'),
            classname='collapsible'
        ),
        MultiFieldPanel(
            [
                FieldPanel('show_images'),
                FieldPanel('show_captions'),
                FieldPanel('show_meta'),
                FieldPanel('show_preview_text'),
            ],
            heading=_('Child page display'),
            classname='collapsible'
        )
    ]

    promote_panels = WebPage.promote_panels + [
        MultiFieldPanel(
            [
                FieldPanel('rss_main_entity'),
                FieldPanel('rss_title'),
                ImageChooserPanel('rss_image'),
                ImageChooserPanel('rss_premium_image'),
                FieldPanel('rss_ttl'),
                FieldPanel('rss_description', widget=SummernoteWidget(attrs={'summernote': {'toolbar': [
                    ['para', ['ul', 'paragraph']],
                    ['insert', ['link']],
                    ['view', ['fullscreen', 'codeview', 'help']],
                ]}})),
                FieldPanel('rss_itunes_primary_category'),
                FieldPanel('rss_itunes_primary_subcategory'),
                FieldPanel('rss_itunes_secondary_category'),
                FieldPanel('rss_itunes_secondary_subcategory'),
                FieldPanel('rss_itunes_explicit'),
                FieldPanel('rss_itunes_type'),
                FieldPanel('rss_combine_private'),
                FieldPanel('rss_include_episode_number'),
                FieldPanel('rss_preview_text'),
                FieldPanel('rss_omit_previews'),
            ],
            heading=_('Required RSS Info')
        ),
        MultiFieldPanel(
            [
                FieldPanel('rss_itunes_title'),
                FieldPanel('rss_itunes_description', widget=forms.Textarea), 
                FieldPanel('rss_google_category'),
                FieldPanel('rss_itunes_author'),
                FieldPanel('rss_itunes_owner'),
                FieldPanel('rss_itunes_owner_email'),
                FieldPanel('rss_itunes_copyright'),
            ],
            heading=_('Optional RSS Info')
        ),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        try:
            all_children = self.get_index_children()
        except:
            all_children = None

        if all_children and all_children.first().season_number and self.rss_itunes_type == 'serial':
            from website.utils import LocalPaginator
            from website.utils import LocalPage
            oldest_season = all_children.first().season_number
            loop_end = all_children.last().season_number
            season_qs = dict()
            for i in range(oldest_season, loop_end + 1):
                season_qs[i] = LocalPaginator(all_children.filter(season_number=i), 200)
                if i > oldest_season:
                    season_qs[i].has_previous = True
                    season_qs[i].previous_page_number = i - 1
                    season_qs[i].num_pages = loop_end
                if i < loop_end:
                    season_qs[i].has_next = True
                    season_qs[i].next_page_number = i + 1
                    season_qs[i].num_pages = loop_end
                season_qs[i].number = i

            pagenum = request.GET.get('p', 1)

            if pagenum == 'latest':
                try:
                    paged_series_children = season_qs.get(loop_end).page(1)
                except (PageNotAnInteger, EmptyPage, InvalidPage) as e:
                    paged_series_children = season_qs[count(season_qs)].page(1)
            else:
                try:
                    paged_series_children = season_qs.get(int(pagenum)).page(1)
                except (PageNotAnInteger, EmptyPage, InvalidPage) as e:
                    paged_series_children = season_qs[count(season_qs)].page(1)

            context['index_paginated'] = paged_series_children
            context['index_children'] = all_children
            
            
        else:
            paginator = Paginator(all_children, self.index_num_per_page)

            pagenum = request.GET.get('p', 1)
            try:
                paged_children = paginator.page(pagenum)
            except (PageNotAnInteger, EmptyPage, InvalidPage) as e:
                paged_children = paginator.page(1)

            context['index_paginated'] = paged_children
            context['index_children'] = all_children

        if request.GET.get('tag', None):
            tags = request.GET.get('tag')
            all_children = all_children.filter(tags__slug__in=[tags])
            context["has_tags"] = True 
            context["index_paginated"] = all_children

        return context

    def clean(self, *args, **kwargs):
        """Translate ttl from HH:MM to MM if necessary"""
        cleaned_data = super().clean()

        if self.rss_ttl:
            ttl = sum(int(x) * 60 ** i for i, x in enumerate(reversed(self.rss_ttl.split(':'))))
            self.rss_ttl = ttl
        else:
            self.rss_ttl = None

        return cleaned_data

    def get_sitemap_urls(self, request=None):
        if self.rss_itunes_type == 'serial':
            all_children = self.get_index_children().order_by('first_published_at')
            if all_children.first().season_number and self.rss_itunes_type == 'serial':
                oldest_season = all_children.first().season_number
                loop_end = all_children.last().season_number
                season_qs = dict()
                season_list = []
                for i in range(oldest_season, loop_end + 1):
                    season_qs[i] = all_children.filter(season_number=i).order_by('-latest_revision_created_at').first()
                    season_qs[i].location = self.get_full_url(request) + '?p=' + str(season_qs[i].season_number)
                    season_qs[i].lastmod = season_qs[i].latest_revision_created_at
                    season_list.append({
                        'location': season_qs[i].location,
                        'lastmod': season_qs[i].lastmod,
                    })

                return season_list
        else:
            return [
                {
                    'location': self.get_full_url(request),
                    # fall back on latest_revision_created_at if last_published_at is null
                    # (for backwards compatibility from before last_published_at was added)
                    'lastmod': (self.last_published_at or self.latest_revision_created_at),
                }
            ]

    @property
    def is_podcast_index(self):

        return True

    @cache_page
    @route(r'^rss/$', name='rss')
    def rss_feed(self, request):
        """
        Renders a public RSS Feed for the public podcast episodes under this page.
        """
        querymodel = resolve_model_string(self.index_query_pagemodel, self._meta.app_label)

        public = exclude_variants(querymodel.objects.child_of(self)).live().order_by('-date_display')
        if self.rss_omit_previews:
            all_public = public.exclude(episode_preview=True)
        else:
            all_public = public
        all_private = None
        rss_link = request.get_raw_uri()
        home_link = self.get_site().root_url
        token = None
        uidb64 = None


        # Construct the feed by passing ourself to it, so it can determine the feed's "link".
        feed = PodcastFeed(request, rss_link, home_link, all_public, all_private, token, uidb64)
        # 'feed' is a class-based view, so we need to call feed and pass it the request to get our response.

        return feed(request)

    
    @cache_control(private=True)
    @nocache_page
    @route(r'^premiumfeed/(?P<uidb64>[-\w]*)/(?P<token>[-\w]*)/$', name='premium_podcast_feed')
    def premium_feed(self, request, uidb64, token):
        """
        Renders a private RSS Feed for a subscriber to episodes under this page.
        """
        querymodel = resolve_model_string(self.index_query_pagemodel, self._meta.app_label)

        try:
            user = UserModel.objects.get(email=urlsafe_base64_decode(uidb64).decode())
        except:
            user = None
        if user and premium_token.check_token(user, token):
            if user.stripe_subscription.plan.product.metadata['tier'] and user.stripe_subscription.status == 'active':

                try:
                    public_queryset = exclude_variants(querymodel.objects.child_of(self).live().order_by('-date_display'))
                except:
                    public_queryset = None

                if public_queryset:
                    user_gte_tiers = []
                    user_eq_tiers = []

                    self.user = user

                    try:
                        tier_gte_objects = TierEqualOrGreater.objects.all()
                    except:
                        tier_gte_objects = None

                    try:
                        tier_eq_objects = TierEqual.objects.all()
                    except:
                        tier_eq_objects = None

                    if tier_gte_objects:
                        for obj in tier_gte_objects:
                            if obj.test_user(self):
                                user_gte_tiers += [obj.segment_id]

                    if tier_eq_objects:
                        for obj in tier_eq_objects:
                            if obj.test_user(self):
                                user_eq_tiers += [obj.segment_id]

                    private_queryset_pages = querymodel.objects.none()
                    public_queryset_pages = querymodel.objects.none()

                    if tier_gte_objects and tier_eq_objects:
                        for tier in user_gte_tiers:
                            public_queryset_pages |= TierEqualOrGreater.segment.get_queryset().get(id=tier).get_used_pages().values_list('canonical_page_id')
                            private_queryset_pages |= TierEqualOrGreater.segment.get_queryset().get(id=tier).get_used_pages().values_list('variant_id')
                        for tier in user_eq_tiers:
                            public_queryset_pages |= TierEqual.segment.get_queryset().get(id=tier).get_used_pages().values_list('canonical_page_id')
                            private_queryset_pages |= TierEqual.segment.get_queryset().get(id=tier).get_used_pages().values_list('variant_id')
                    elif tier_gte_objects and not tier_eq_objects:
                        for tier in user_gte_tiers:
                            public_queryset_pages |= TierEqualOrGreater.segment.get_queryset().get(id=tier).get_used_pages().values_list('canonical_page_id')
                            private_queryset_pages |= TierEqualOrGreater.segment.get_queryset().get(id=tier).get_used_pages().values_list('variant_id')
                    elif tier_eq_objects and not tier_gte_objects:
                        for tier in user_eq_tiers:
                            public_queryset_pages |= TierEqual.segment.get_queryset().get(id=tier).get_used_pages().values_list('canonical_page_id')
                            private_queryset_pages |= TierEqual.segment.get_queryset().get(id=tier).get_used_pages().values_list('variant_id')
                    else:
                        private_queryset_pages = None
                        public_queryset_pages = None

                    if self.rss_combine_private:
                        queryset_public = public_queryset.filter(~Q(id__in=public_queryset_pages)).filter(parent_page=self.id).order_by('-date_display')
                        queryset_private = querymodel.objects.filter(Q(id__in=private_queryset_pages)).filter(parent_page=self.id).live().order_by('-date_display')
                        queryset = queryset_private | queryset_public
                    else:
                        queryset = querymodel.objects.filter(Q(id__in=private_queryset_pages)).filter(parent_page=self.id).live().order_by('-date_display')

                    all_public = queryset_public if self.rss_combine_private else None
                    all_private = queryset
                    rss_link = request.get_raw_uri()
                    home_link = self.get_site().root_url

                    # Construct the feed by passing ourself to it, so it can determine the feed's "link".
                    feed = PodcastFeed(request, rss_link, home_link, all_public, all_private, token, uidb64)
                    # 'feed' is a class-based view, so we need to call feed and pass it the request to get our response.
                    return feed(request)
                else:
                    return HttpResponseForbidden()
            else:
                return HttpResponseForbidden()
        else:
            return HttpResponseForbidden()

    def serve(self, request, *args, **kwargs):
        request.is_preview = getattr(request, 'is_preview', False)

        if not request.GET and (self.rss_itunes_type == 'serial'):
            path = request.path_info.strip('/')
            slug = self.slug
            if path == slug:
                latest_episode = self.get_index_children().first()
                season = str(latest_episode.season_number)
                return redirect(str(request.get_raw_uri()) + '?p=' + season, permanent=False)
   
        return super().serve(request, *args, **kwargs)

class ArticleContentIndexPage(WagtailCacheMixin, RoutablePageMixin, WebPage):
    """
    Shows a list of content sub-pages.
    """

    def get_author_list():
        g = Group.objects.get(name='Authors')
        return {'groups__in': [g, ]}

    class Meta:
        verbose_name = _('Index Page for Articles')
        abstract = False

    index_query_pagemodel = 'website.ArticleContentPage'
    index_show_subpages_default = True

    index_order_by_default = '-date_display'
    index_order_by_choices = (('-date_display', 'Display publish date, newest first'),) + \
        WebPage.index_order_by_choices

    parent_page_types = ['website.GenericPage']

    subpage_types = ['website.ArticleContentPage']

    template = 'website/pages/content_index_page.html'

    show_images = models.BooleanField(
        default=True,
        verbose_name=_('Show images'),
    )
    show_captions = models.BooleanField(
        default=True,
    )
    show_meta = models.BooleanField(
        default=True,
        verbose_name=_('Show author and date info'),
    )
    show_preview_text = models.BooleanField(
        default=True,
        verbose_name=_('Show preview text'),
    )

    rss_main_entity = models.BooleanField(
        choices=page_choices['BOOLEAN_CHOICES'],
        verbose_name=_('Main entity of the site?'),
        help_text=_('Works with site settings SEO data: is this the primary media production of this site?'),
        db_index=True
    )

    rss_ttl = models.CharField(
        max_length=10,
        verbose_name=_('RSS TTL'),
        help_text=_('The RSS channel time to live (cache), or estimated time between articles. Valid entries: HH:MM and MM.')
    )

    rss_title = models.CharField(
        verbose_name=_('RSS Title'),
        max_length=255,
        help_text=_('The RSS channel title (required).')
    )

    rss_description = models.TextField(
        null=False,
        blank=False,
        default=' ',
        verbose_name=_('RSS Description'),
        help_text=_('The RSS main channel description (required).')
    )

    rss_categories = models.BooleanField(
        choices=page_choices['BOOLEAN_CHOICES'],
        max_length=10,
        verbose_name=_('Categorize RSS'),
        help_text=_('If enabled, will use the tag(s) (under "classify" tab) as your RSS category(s). Article child pages will also be categorized by their tag(s) if enabled.')
    )

    rss_combine_private = models.BooleanField(
        choices=page_choices['BOOLEAN_CHOICES'],
        verbose_name=_('Combine Feeds'),
        help_text=_('Combine private and public feed for subscribers, so that they can unfollow/unsubscribe the public feed.')
    )

    rss_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_('RSS image'),
        help_text=_('RSS channel logo image, PNG or JPEG.')
    )

    rss_premium_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_('RSS premium image'),
        help_text=_('The RSS image which will appear for premium feed users on the paid tier(s)')
    )

    rss_author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        max_length=50,
        related_name='+',
        limit_choices_to=get_author_list,
        on_delete=models.SET_NULL,
        verbose_name=_('RSS author'),
        help_text=_('Optional, will set the RSS author. Warning: denotes an email, so the email will be made public.')
    )

    rss_editor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        max_length=50,
        related_name='+',
        limit_choices_to=get_author_list,
        on_delete=models.SET_NULL,
        verbose_name=_('RSS editor'),
        help_text=_('Optional, editor contact. Warning: denotes an email, so the email will be made public.')
    )

    rss_copyright = models.CharField(
        blank=True,
        null=True,
        max_length=75,
        verbose_name=_('RSS copyright'),
        help_text=_('Optional, custom RSS copyright name / organization. If omitted, will default to the feed title. DO NOT PUT DATES, they are auto-calculated.')
    )

    layout_panels = WebPage.layout_panels + [
        MultiFieldPanel(
            [
                FieldPanel('index_show_subpages'),
                FieldPanel('index_num_per_page'),
                FieldPanel('index_order_by'),
            ],
            heading=_('Show Child Pages'),
            classname='collapsible'
        ),
        MultiFieldPanel(
            [
                FieldPanel('show_images'),
                FieldPanel('show_captions'),
                FieldPanel('show_meta'),
                FieldPanel('show_preview_text'),
            ],
            heading=_('Child page display'),
            classname='collapsible'
        )
    ]

    promote_panels = WebPage.promote_panels + [
        MultiFieldPanel(
            [
                FieldPanel('rss_main_entity'),
                FieldPanel('rss_title'),
                ImageChooserPanel('rss_image'),
                ImageChooserPanel('rss_premium_image'),
                FieldPanel('rss_ttl'),
                FieldPanel('rss_description', widget=SummernoteWidget(attrs={'summernote': {'toolbar': [
                    ['para', ['ul', 'paragraph']],
                    ['insert', ['link']],
                    ['view', ['fullscreen', 'codeview', 'help']],
                ]}})),
                FieldPanel('rss_combine_private'),
                FieldPanel('rss_categories'),
            ],
            heading=_('Required RSS Info')
        ),
        MultiFieldPanel(
            [
                FieldPanel('rss_author'), 
                FieldPanel('rss_editor'),
                FieldPanel('rss_copyright'),
            ],
            heading=_('Optional RSS Info')
        ),
    ]

    @property
    def is_article_index(self):

        return True

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        all_children = self.get_index_children()
        paginator = Paginator(all_children, self.index_num_per_page)

        pagenum = request.GET.get('p', 1)
        try:
            paged_children = paginator.page(pagenum)
        except (PageNotAnInteger, EmptyPage, InvalidPage) as e:
            paged_children = paginator.page(1)

        context['index_paginated'] = paged_children
        context['index_children'] = all_children

        if request.GET.get('tag', None):
            context['has_tags'] = True
            tags = request.GET.get('tag')
            all_children = all_children.filter(tags__slug__in=[tags])
            context['index_paginated'] = all_children
        else:
            context['index_paginated'] = paged_children

        return context

    @cache_page
    @route(r'^rss/$', name='rss')
    def rss_feed(self, request):
        """
        Renders a public RSS Feed for the public articles under this page.
        """

        querymodel = resolve_model_string(self.index_query_pagemodel, self._meta.app_label)

        all_public = exclude_variants(querymodel.objects.child_of(self)).live().order_by('-date_display')
        all_private = None
        rss_link = request.get_raw_uri()
        home_link = self.get_site().root_url
        tags = self.tags.all() if self.tags.first() else None
        token = None
        uidb64 = None

        # Construct the feed by passing ourself to it, so it can determine the feed's "link".
        feed = ArticleFeed(request, rss_link, home_link, all_public, all_private, tags, uidb64, token)
        # 'feed' is a class-based view, so we need to call feed and pass it the request to get our response.
        return feed(request)

    @cache_control(private=True)
    @nocache_page
    @route(r'^premiumfeed/(?P<uidb64>[-\w]*)/(?P<token>[-\w]*)/$', name='premiumfeed')
    def premium_feed(self, request, uidb64, token):
        """
        Renders a private RSS Feed for a subscriber to episodes under this page.
        """
        querymodel = resolve_model_string(self.index_query_pagemodel, self._meta.app_label)

        try:
            user = UserModel.objects.get(email=urlsafe_base64_decode(uidb64).decode())
        except:
            user = None
        if user and premium_token.check_token(user, token):
            if user.stripe_subscription.plan.product.metadata['tier'] and user.stripe_subscription.status == 'active':

                try:
                    public_queryset = exclude_variants(querymodel.objects.child_of(self).live()).order_by('-date_display')
                except:
                    public_queryset = None

                if public_queryset:
                    user_gte_tiers = []
                    user_eq_tiers = []
                    queryset = ArticleContentPage.objects.none()
                    self.user = user

                    try:
                        tier_gte_objects = TierEqualOrGreater.objects.all()
                    except:
                        tier_gte_objects = None

                    try:
                        tier_eq_objects = TierEqual.objects.all()
                    except:
                        tier_eq_objects = None

                    if tier_gte_objects:
                        for obj in tier_gte_objects:
                            if obj.test_user(self):
                                user_gte_tiers += [obj.segment_id]

                    if tier_eq_objects:
                        for obj in tier_eq_objects:
                            if obj.test_user(self):
                                user_eq_tiers += [obj.segment_id]

                    private_queryset_pages = querymodel.objects.none()
                    public_queryset_pages = querymodel.objects.none()

                    if tier_gte_objects and tier_eq_objects:
                        for tier in user_gte_tiers:
                            public_queryset_pages |= TierEqualOrGreater.segment.get_queryset().get(id=tier).get_used_pages().values_list('canonical_page_id')
                            private_queryset_pages |= TierEqualOrGreater.segment.get_queryset().get(id=tier).get_used_pages().values_list('variant_id')
                        for tier in user_eq_tiers:
                            public_queryset_pages |= TierEqual.segment.get_queryset().get(id=tier).get_used_pages().values_list('canonical_page_id')
                            private_queryset_pages |= TierEqual.segment.get_queryset().get(id=tier).get_used_pages().values_list('variant_id')
                    elif tier_gte_objects and not tier_eq_objects:
                        for tier in user_gte_tiers:
                            public_queryset_pages |= TierEqualOrGreater.segment.get_queryset().get(id=tier).get_used_pages().values_list('canonical_page_id')
                            private_queryset_pages |= TierEqualOrGreater.segment.get_queryset().get(id=tier).get_used_pages().values_list('variant_id')
                    elif tier_eq_objects and not tier_gte_objects:
                        for tier in user_eq_tiers:
                            public_queryset_pages |= TierEqual.segment.get_queryset().get(id=tier).get_used_pages().values_list('canonical_page_id')
                            private_queryset_pages |= TierEqual.segment.get_queryset().get(id=tier).get_used_pages().values_list('variant_id')
                    else:
                        private_queryset_pages = None
                        public_queryset_pages = None

                    if self.rss_combine_private:
                         queryset_public = public_queryset.filter(~Q(id__in=public_queryset_pages)).filter(parent_page=self.id).order_by('-date_display')
                         queryset_private = querymodel.objects.filter(Q(id__in=private_queryset_pages)).filter(parent_page=self.id).live().order_by('-date_display')
                         queryset = queryset_private | queryset_public
                    else:
                         queryset = querymodel.objects.filter(Q(id__in=private_queryset_pages)).filter(parent_page=self.id).live().order_by('-date_display')

                    all_public = queryset_public if self.rss_combine_private else None
                    all_private = queryset
                    rss_link = request.get_raw_uri()
                    home_link = self.get_site().root_url
                    tags = self.tags.all() if self.tags.first() else None

                    # Construct the feed by passing ourself to it, so it can determine the feed's "link".
                    feed = ArticleFeed(request, rss_link, home_link, all_public, all_private, tags, uidb64, token)
                    # 'feed' is a class-based view, so we need to call feed and pass it the request to get our response.
                    return feed(request)
                else:
                    return HttpResponseForbidden()
            else:
                return HttpResponseForbidden()
        else:
            return HttpResponseForbidden()


class ArticleContentPage(WagtailCacheMixin, PersonalisablePageMixin, WebPage):
    """
    Content, suitable for news articles.
    """
    class Meta:
        verbose_name = _('Article Post Page')
        abstract = False

    parent_page_types = ['website.ArticleContentIndexPage']

    subpage_types = []

    exclude_fields_in_copy = [
            'comments', 
            'episode_type', 
            'guid', 
            'remote_media', 
            'remote_media_duration', 
            'remote_media_thumbnail', 
            'remote_media_type', 
            'remote_media_size', 
            'uploaded_media', 
            'uploaded_media_type',
            'tagged_items',
            'author',
            'contributor',
            'seo_title',
            'search_description'
        ]

    template = 'website/pages/content_page.html'
    search_template = 'search/content_page_search.html'

    unique_together = [
            ['uploaded_media', 'remote_media'],  
            ['uploaded_media_type', 'remote_media_type']
        ]
        # todo, a clever set of constraints that pass wagtail's draft save which
        # prevent people from having both a local and a remote episode. As of this
        # version, wagtail only supports 'unique_together' in its UI, so we use it.
        #constraints = [
        #    constraints.CheckConstraint(
        #        name="%(app_label)s_%(class)s_uploaded_media_or_remote_media",
        #        check=(
        #            Q(uploaded_media__isnull=True, remote_media__isnull=False)
        #            | Q(uploaded_media__isnull=False, remote_media__isnull=True)
        #        ),
        #    )
        #]

    search_fields = (
        WebPage.search_fields + [
            index.SearchField('caption', boost=2),
            index.FilterField('date_display'),
            index.RelatedFields('contributor', [
                index.SearchField('contributor'),
                index.SearchField('contributor_display'),
            ]),
            index.RelatedFields('author', [
                index.SearchField('author'),
                index.SearchField('author_display'),
            ]),
            index.RelatedFields('tags', [
                index.SearchField('name', partial_match=True, boost=10),
            ]),
        ]
    )

    # Override body to provide simpler content
    body = StreamField(contentpage_streamblocks, null=True, blank=True, verbose_name='', help_text='', block_counts={
        'body_text': {'min_num': 1, 'max_num': 1},
        'local_media': {'max_num': 1},
        'authors_contributors': {'max_num': 1},
        'title_heading': {'max_num': 1},
        'user_comments': {'max_num': 1},
    })
    front_page = models.BooleanField(
        blank=False,
        null=False,
        default=True,
        choices=page_choices['BOOLEAN_CHOICES'],
        verbose_name=_('Front page?'),
        help_text=_('Show on home page list?')
    )
    caption = models.CharField(
        blank=False,
        max_length=255,
        verbose_name=_('Caption'),
    )

    date_display = models.DateField(
        blank=False,
        default=datetime.now,
        verbose_name=_('Publish date'),
    )

    guid = models.UUIDField(
        default=uuid.uuid4,
        unique=False,
        editable=False,
    )

    uploaded_media = models.ForeignKey(
        settings.WAGTAILMEDIA['MEDIA_MODEL'],
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_('Uploaded episode'),
        help_text=_('Embed a locally uploaded episode.')
    )
    uploaded_media_type = models.CharField(
        blank=True,
        null=True,
        verbose_name=_('Uploaded file type'),
        max_length=25,
        help_text=_('Uploaded media content type.'),
    )
    remote_media = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('External episode'),
        help_text=_('Optionally, link a remote episode.'),
    )
    remote_media_thumbnail = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_('External thumbnail'),
        help_text=_('Remote media thumbnail image, if blank defaults to the main RSS feed image.'),
    )
    remote_media_type = models.CharField(
        blank=True,
        null=True,
        verbose_name=_('External type'),
        choices=page_choices['MEDIA_CONTENT_TYPE_CHOICES'],
        max_length=25,
        help_text=_('Remote media content type, leave blank for locally uploaded media.'),
    )
    remote_media_size = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Remote file size'),
        help_text=_('Length in seconds of remote media, for RSS feed information.')
    )
    remote_media_duration = models.CharField(
        blank=True,
        null=True,
        max_length=15,
        verbose_name=_('File duration'),
        help_text=_('Length in seconds of remote media, for RSS feed information. Valid formats: HH:MM:SS, MM:SS, or SS')
    )

    parent_page = models.ForeignKey(
        'website.ArticleContentIndexPage',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def get_pub_date(self):
        """
        Gets published date.
        """
        if self.date_display:
            return self.date_display
        return ''

    def get_description(self):
        """
        Gets the description using a fallback.
        """
        if self.search_description:
            return self.search_description
        if self.caption:
            return self.caption
        if self.body_preview:
            return self.body_preview
        return ''

    def clean(self, *args, **kwargs):
        """
        Make sure user isn't trying to embed two media files.
        Make sure there's a valid duration for the RSS feed for
        whatever type of media file the user has included.
        """
        cleaned_data = super().clean()

        if self.remote_media_duration:
            duration = sum(int(x) * 60 ** i for i, x in enumerate(reversed(self.remote_media_duration.split(':'))))
            self.remote_media_duration = duration
        else:
            self.remote_media_duration = None

        if self.uploaded_media and self.remote_media:
            raise ValidationError({'uploaded_media': 'You can only have remote OR uploaded media outside the main page body, not both.'})
        if self.remote_media and not self.remote_media_duration:
            if self.remote_media_type != 'vimeo' and self.remote_media_type != 'youtube':
                raise ValidationError({'remote_media_duration': 'You must provide a valid duration.'})
            else:
                pass

        return cleaned_data

    def save(self, *args, **kwargs):
        """
        Collect additional info on the media to be embedded for RSS purposes and store it.
        """
        if self.uploaded_media:
            extension = self.uploaded_media.file_extension
            if self.uploaded_media.type == 'audio':
                if extension == 'm4a' or extension == 'aac' or extension == 'mp4':
                    self.uploaded_media_type = 'audio/x-m4a'
                elif extension == 'mp3':
                    self.uploaded_media_type = 'audio/mpeg'
                elif extension == 'oga' or extension == 'ogg':
                    self.uploaded_media_type = 'audio/ogg'
                elif extension == 'wav':
                    self.uploaded_media_type = 'audio/wav'
            elif self.uploaded_media.type == 'video':
                if extension == 'mp4' or extension == 'm4v':
                    self.uploaded_media_type = 'video/x-m4v'
                elif extension == 'ogv' or extension == 'ogg':
                    self.uploaded_media_type = 'video/ogg'
                elif extension == '3gp':
                    self.uploaded_media_type = 'video/3gpp'
                elif extension == 'webm':
                    self.uploaded_media_type = 'video/webm'
            else:
                self.uploaded_media_type = ''
            self.remote_media = None
            self.remote_media_type = None
            self.remote_media_size = None
            self.remote_media_duration = None

        if self.remote_media:
            try:
                size = requests.get(self.remote_media, stream=True).headers['content-length']
            except:
                size = None
            extension = pathlib.Path(self.remote_media).suffix.split('.')[-1]
            self.uploaded_media = None
            self.uploaded_media_type = None
            self.uploaded_media_size = None
            self.remote_media_size = size
        self.parent_page = self.get_parent().specific

        super().save()

    content_panels = WebPage.content_panels + [
        FieldPanel('front_page'),
        FieldPanel('caption'),
        FieldPanel('date_display'),
        MultiFieldPanel(
            [
                InlinePanel('author', label="Author/Host/Creator"),
                InlinePanel('contributor', label="Contributor"),
            ],
            _('Author Info'),
            classname='collapsible'
        ),
        MultiFieldPanel(
            [
                MediaChooserPanel('uploaded_media'),
            ],
            _('Embedded Media'),
            classname='collapsible'
        ),
        MultiFieldPanel(
            [
                FieldPanel('remote_media'),
                FieldPanel('remote_media_type'),
                FieldPanel('remote_media_duration'),
                ImageChooserPanel('remote_media_thumbnail'),
            ],
            _('Remote Media'),
            classname='collapsible'
        ),
    ]
    body_content_panels = [
        MultiFieldPanel(
            [
                StreamFieldPanel('body'),
            ],
            _('Page Body'),
            classname='collapsible'
        ),
    ]

class PodcastContentPage(WagtailCacheMixin, PersonalisablePageMixin, WebPage):
    """
    Content, suitable for podcast episodes.
    """

    class Meta:
        verbose_name = _('Podcast Episode Page')
        abstract = False

    parent_page_types = ['website.PodcastContentIndexPage']

    subpage_types = []

    exclude_fields_in_copy = [
            'comments', 
            'guid', 
            'remote_media', 
            'remote_media_duration', 
            'remote_media_thumbnail', 
            'remote_media_type', 
            'remote_media_size', 
            'uploaded_media', 
            'uploaded_media_type',
            'tagged_items',
            'author',
            'contributor',
            'seo_title',
            'search_description'
        ]

    template = 'website/pages/content_page.html'
    search_template = 'search/content_page_search.html'

    unique_together = [
            ['uploaded_media', 'remote_media'],  
            ['uploaded_media_type', 'remote_media_type']
        ]
        # todo, a clever set of constraints that pass wagtail's draft save which
        # prevent people from having both a local and a remote episode. As of this
        # version, wagtail only supports 'unique_together' in its UI, so we use it.
        #constraints = [
        #    constraints.CheckConstraint(
        #        name="%(app_label)s_%(class)s_uploaded_media_or_remote_media",
        #        check=(
        #            Q(uploaded_media__isnull=True, remote_media__isnull=False)
        #            | Q(uploaded_media__isnull=False, remote_media__isnull=True)
        #        ),
        #    )
        #]

    search_fields = (
        WebPage.search_fields + [
            index.SearchField('caption', boost=2),
            index.FilterField('date_display'),
            index.RelatedFields('contributor', [
                index.SearchField('contributor'),
                index.SearchField('contributor_display'),
            ]),
            index.RelatedFields('author', [
                index.SearchField('author'),
                index.SearchField('author_display'),
            ]),
            index.RelatedFields('tags', [
                index.SearchField('name', partial_match=True, boost=10),
            ]),
        ]
    )

    # Override body to provide simpler content
    body = StreamField(contentpage_streamblocks, null=True, blank=True, verbose_name='', help_text='', block_counts={
        'body_text': {'min_num': 1, 'max_num': 1},
        'local_media': {'max_num': 1},
        'authors_contributors': {'max_num': 1},
        'title_heading': {'max_num': 1},
        'user_comments': {'max_num': 1},
    })
    front_page = models.BooleanField(
        blank=False,
        null=False,
        default=True,
        choices=page_choices['BOOLEAN_CHOICES'],
        verbose_name=_('Front page?'),
        help_text=_('Show on home page list?')
    )

    episode_number = models.SmallIntegerField(
        blank=True,
        null=True,
        verbose_name=_('Episode number'),
        help_text=_('Episode number, used in RSS feed generation.')
    )

    episode_type = models.CharField(
        blank=True,
        null=True,
        max_length=10,
        choices=(('bonus', 'Bonus'), ('trailer', 'Trailer')),
        verbose_name=_('Episode type'),
        help_text=_('Optional, is this a bonus? Or a trailer episode outside the normal sequence? Leave blank if neither.')
    )

    season_number = models.SmallIntegerField(
        blank=True,
        null=True,
        verbose_name=_('Season number'),
        help_text=_('Optional, if your show is categorized by seasons, specify the season this one is in, otherwise leave blank.'),
        db_index=True
    )

    uploaded_media = models.ForeignKey(
        settings.WAGTAILMEDIA['MEDIA_MODEL'],
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_('Uploaded episode'),
        help_text=_('Embed a locally uploaded episode.')
    )
    uploaded_media_type = models.CharField(
        blank=True,
        null=True,
        verbose_name=_('Uploaded file type'),
        max_length=25,
        help_text=_('Uploaded media content type.'),
    )
    remote_media = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('External episode'),
        help_text=_('Optionally, link a remote episode.'),
    )
    remote_media_thumbnail = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_('External thumbnail'),
        help_text=_('Remote media thumbnail image, if blank defaults to the main RSS feed image.'),
    )
    remote_media_type = models.CharField(
        blank=True,
        null=True,
        verbose_name=_('External type'),
        choices=page_choices['MEDIA_CONTENT_TYPE_CHOICES'],
        max_length=25,
        help_text=_('Remote media content type, leave blank for locally uploaded media.'),
    )
    remote_media_size = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_('Remote file size'),
        help_text=_('Length in seconds of remote media, for RSS feed information.')
    )
    remote_media_duration = models.CharField(
        blank=True,
        null=True,
        max_length=15,
        verbose_name=_('File duration'),
        help_text=_('Length in seconds of remote media, for RSS feed information. Valid formats: HH:MM:SS, MM:SS, or SS')
    )

    caption = models.CharField(
        blank=False,
        max_length=255,
        verbose_name=_('Caption'),
    )

    date_display = models.DateField(
        blank=False,
        default=datetime.now,
        verbose_name=_('Publish date'),
    )
    guid = models.UUIDField(
        default=uuid.uuid4,
        unique=False,
        editable=False,
    )

    parent_page = models.ForeignKey(
        'website.PodcastContentIndexPage',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    episode_preview = models.BooleanField(
        max_length=50,
        blank=False,
        null=False,
        choices=page_choices['BOOLEAN_CHOICES'],
        verbose_name=_('Preview?'),
        help_text=_('Is this a preview of a paid episode the public feed? This controls the RSS preview prefix setting.')
    )

    def get_pub_date(self):
        """
        Gets published date.
        """
        if self.date_display:
            return self.date_display
        return ''

    def get_description(self):
        """
        Gets the description using a fallback.
        """
        if self.search_description:
            return self.search_description
        if self.caption:
            return self.caption
        if self.body_preview:
            return self.body_preview
        return ''

    def clean(self, *args, **kwargs):
        """
        Make sure user isn't trying to embed two media files.
        Make sure there's a valid duration for the RSS feed for
        whatever type of media file the user has included.
        """
        cleaned_data = super().clean()

        if self.remote_media_duration:
            duration = sum(int(x) * 60 ** i for i, x in enumerate(reversed(self.remote_media_duration.split(':'))))
            self.remote_media_duration = duration
        else:
            self.remote_media_duration = None

        if self.uploaded_media and self.remote_media:
            raise ValidationError({'uploaded_media': 'You can only have remote OR uploaded media outside the main page body, not both.'})
        if self.remote_media and not self.remote_media_duration:
            if self.remote_media_type != 'vimeo' and self.remote_media_type != 'youtube':
                raise ValidationError({'remote_media_duration': 'You must provide a valid duration.'})
            else:
                pass

        return cleaned_data

    def save(self, *args, **kwargs):
        """
        Collect additional info on the media to be embedded for RSS purposes and store it.
        """
        if self.uploaded_media:
            extension = self.uploaded_media.file_extension
            if self.uploaded_media.type == 'audio':
                if extension == 'm4a' or extension == 'aac' or extension == 'mp4':
                    self.uploaded_media_type = 'audio/x-m4a'
                elif extension == 'mp3':
                    self.uploaded_media_type = 'audio/mpeg'
                elif extension == 'oga' or extension == 'ogg':
                    self.uploaded_media_type = 'audio/ogg'
                elif extension == 'wav':
                    self.uploaded_media_type = 'audio/wav'
            elif self.uploaded_media.type == 'video':
                if extension == 'mp4' or extension == 'm4v':
                    self.uploaded_media_type = 'video/x-m4v'
                elif extension == 'ogv' or extension == 'ogg':
                    self.uploaded_media_type = 'video/ogg'
                elif extension == '3gp':
                    self.uploaded_media_type = 'video/3gpp'
                elif extension == 'webm':
                    self.uploaded_media_type = 'video/webm'
            else:
                self.uploaded_media_type = ''
            self.remote_media = None
            self.remote_media_type = None
            self.remote_media_size = None
            self.remote_media_duration = None

        if self.remote_media:
            try:
                size = requests.get(self.remote_media, stream=True).headers['content-length']
            except:
                size = None
            extension = pathlib.Path(self.remote_media).suffix.split('.')[-1]
            self.uploaded_media = None
            self.uploaded_media_type = None
            self.uploaded_media_size = None
            self.remote_media_size = size
        self.parent_page = self.get_parent().specific

        super().save()

    content_panels = WebPage.content_panels + [
        FieldPanel('episode_number'),
        FieldPanel('episode_type'),
        FieldPanel('episode_preview'),
        FieldPanel('front_page'),
        FieldPanel('caption'),
        FieldPanel('date_display'),
        MultiFieldPanel(
            [
                InlinePanel('author', label="Author/Host/Creator"),
                InlinePanel('contributor', label="Contributor"),
            ],
            _('Author Info'),
            classname='collapsible'
        ),
        MultiFieldPanel(
            [
                MediaChooserPanel('uploaded_media'),
            ],
            _('Embedded Media'),
            classname='collapsible'
        ),
        MultiFieldPanel(
            [
                FieldPanel('remote_media'),
                FieldPanel('remote_media_type'),
                FieldPanel('remote_media_duration'),
                ImageChooserPanel('remote_media_thumbnail'),
            ],
            _('Remote Media'),
            classname='collapsible'
        ),
    ]
    body_content_panels = [
        MultiFieldPanel(
            [
                StreamFieldPanel('body'),
            ],
            _('Page Body'),
            classname='collapsible'
        ),
        MultiFieldPanel(
            [
                FieldPanel('season_number'),
            ],
            _('Season Info'),
            classname='collapsible collapsed',
        ),
    ]


class FormConfirmEmail(Email):
    """
    Sends a confirmation email after submitting a Basic Form Page.
    """
    page = ParentalKey(
        'BasicFormPage',
        related_name='confirmation_emails'
    )


class StreamFormConfirmEmail(Email):
    """
    Sends a confirmation email after submitting an Advanced Form Page.
    """
    page = ParentalKey(
        'StreamFormPage',
        related_name='confirmation_emails'
    )


class FormBuilder(WagtailFormBuilder):
    """
    Enhance wagtail FormBuilder with additional custom fields.
    """

    def create_date_field(self, field, options):
        return DateField(**options)

    def create_datetime_field(self, field, options):
        return DateTimeField(**options)

    def create_time_field(self, field, options):
        return TimeField(**options)


class FormPageMixin(models.Model):

    class Meta:
        abstract = True

    submissions_list_view_class = SubmissionsListView
    encoder = DjangoJSONEncoder

    # Custom website fields
    to_address = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Email form submissions to'),
        help_text=_('Optional - email form submissions to this address. Separate multiple addresses by comma.'),  # noqa
    )
    reply_address = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Reply-to address'),
        help_text=_('Optional - to reply to the submitter, specify the email field here. For example, if a form field above is labeled "Your Email", enter: {{ your_email }}'),  # noqa
    )
    subject = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Subject'),
    )
    save_to_database = models.BooleanField(
        default=True,
        verbose_name=_('Save form submissions'),
        help_text=_('Submissions are saved to database and can be exported at any time.')
    )
    thank_you_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_('Thank you page'),
        help_text=_('The page users are redirected to after submitting the form.'),
    )
    button_text = models.CharField(
        max_length=255,
        default=_('Submit'),
        verbose_name=_('Button text'),
    )
    button_style = models.CharField(
        blank=True,
        choices=page_choices['BUTTON_STYLE_CHOICES'],
        default=page_choices["BUTTON_STYLE_DEFAULT"],
        max_length=255,
        verbose_name=_('Button style'),
    )
    button_size = models.CharField(
        blank=True,
        choices=page_choices['BUTTON_SIZE_CHOICES'],
        default=page_choices["BUTTON_SIZE_DEFAULT"],
        max_length=255,
        verbose_name=_('Button Size'),
    )
    button_css_class = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Button CSS class'),
        help_text=_('Custom CSS class applied to the submit button.'),
    )
    form_css_class = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Form CSS Class'),
        help_text=_('Custom CSS class applied to <form> element.'),
    )
    form_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Form ID'),
        help_text=_('Custom ID applied to <form> element.'),
    )
    form_golive_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Form go live date/time'),
        help_text=_('Date and time when the FORM goes live on the page.'),
    )
    form_expire_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Form expiry date/time'),
        help_text=_('Date and time when the FORM will no longer be available on the page.'),
    )
    spam_protection = models.BooleanField(
        default=True,
        verbose_name=_('Spam Protection'),
        help_text=_('When enabled, the CMS will filter out spam form submissions for this page.')
    )

    body_content_panels = [
        MultiFieldPanel(
            [
                PageChooserPanel('thank_you_page'),
                FieldPanel('button_text'),
                FieldPanel('button_style'),
                FieldPanel('button_size'),
                FieldPanel('button_css_class'),
                FieldPanel('form_css_class'),
                FieldPanel('form_id'),
            ],
            _('Form Settings'),
            classname='collapsible'
        ),
        MultiFieldPanel(
            [
                FieldPanel('save_to_database'),
                FieldPanel('to_address'),
                FieldPanel('reply_address'),
                FieldPanel('subject'),
            ],
            _('Form Submissions'),
            classname='collapsible'
        ),
    ]

    settings_panels = [
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel('form_golive_at'),
                        FieldPanel('form_expire_at'),
                    ],
                    classname='label-above',
                ),
            ],
            _('Form Scheduled Publishing'),
            classname='collapsible'
        ),
        FieldPanel('spam_protection')
    ]

    @property
    def form_live(self):
        """
        A boolean on whether or not the <form> element should be shown on the page.
        """
        return (self.form_golive_at is None or self.form_golive_at <= timezone.now()) and \
               (self.form_expire_at is None or self.form_expire_at >= timezone.now())

    def get_landing_page_template(self, request, *args, **kwargs):
        return self.landing_page_template

    def process_data(self, form, request):
        processed_data = {}
        # Handle file uploads
        for key, val in form.cleaned_data.items():

            if type(val) == InMemoryUploadedFile or type(val) == TemporaryUploadedFile:
                # Save the file and get its URL

                directory = request.session.session_key
                storage = self.get_storage()
                Path(storage.path(directory)).mkdir(parents=True,
                                                    exist_ok=True)
                path = storage.get_available_name(
                    str(Path(directory) / val.name))
                with storage.open(path, 'wb+') as destination:
                    for chunk in val.chunks():
                        destination.write(chunk)

                processed_data[key] = "{0}{1}".format(page_choices['PROTECTED_MEDIA_URL'], path)
            else:
                processed_data[key] = val

        return processed_data

    def get_storage(self):
        return FileSystemStorage(
            location=page_choices['PROTECTED_MEDIA_ROOT'],
            base_url=page_choices['PROTECTED_MEDIA_URL']
        )

    def process_form_submission(self, request, form, form_submission, processed_data):

        # Save to database
        if self.save_to_database:
            form_submission.save()

        # Send the mails
        if self.to_address:
            self.send_summary_mail(request, form, processed_data)

        if self.confirmation_emails:
            # Convert form data into a context.
            context = Context(self.data_to_dict(processed_data, request))
            # Render emails as if they are django templates.
            for email in self.confirmation_emails.all():

                # Build email message parameters.
                message_args = {}
                # From
                if email.from_address:
                    template_from_email = Template(email.from_address)
                    message_args['from_email'] = template_from_email.render(context)
                else:
                    genemail = GeneralSettings.for_request(request).from_email
                    if genemail:
                        message_args['from_email'] = genemail
                # Reply-to
                if email.reply_address:
                    template_reply_to = Template(email.reply_address)
                    message_args['reply_to'] = template_reply_to.render(context).split(',')
                else:
                    template_reply_to = Template(settings.EMAIL_ADDR)
                    message_args['reply_to'] = template_reply_to.render(context)
                # CC
                if email.cc_address:
                    template_cc = Template(email.cc_address)
                    message_args['cc'] = template_cc.render(context).split(',')
                # BCC
                if email.bcc_address:
                    template_bcc = Template(email.bcc_address)
                    message_args['bcc'] = template_bcc.render(context).split(',')
                # Subject
                if email.subject:
                    template_subject = Template(email.subject)
                    message_args['subject'] = template_subject.render(context)
                else:
                    message_args['subject'] = self.title
                # Body
                template_body = Template(email.body)
                message_args['body'] = template_body.render(context)
                # To
                template_to = Template(email.to_address)
                message_args['to'] = template_to.render(context).split(',')

                mail.send(
                    message_args['to'],
                    message_args['from_email'],
                    subject=message_args['subject'],
                    cc=message_args['cc'] if email.bcc_address else None,
                    bcc=message_args['bcc'] if email.bcc_address else None,
                    html_message=message_args['body'],
                    headers={'Reply-to': message_args['reply_to']}
                )

        for fn in hooks.get_hooks('form_page_submit'):
            fn(instance=self, form_submission=form_submission)

    def send_summary_mail(self, request, form, processed_data):
        """
        Sends a form submission summary email.
        """
        addresses = [x.strip() for x in self.to_address.split(',')]
        content = []

        context = Context(self.data_to_dict(processed_data, request))

        genemail = GeneralSettings.for_request(request).from_email

        # Build email message parameters
        message_args = {
            'body': context['message']
        }

        for address in addresses:

            if self.subject:
                message_args['subject'] = self.subject
            else:
                message_args['subject'] = self.title
            if genemail:
                template_from_email = Template(genemail)
                message_args['from_email'] = template_from_email.render(context)
            else:
                template_from = Template(settings.EMAIL_ADDR)
                message_args['from_email'] = template_from_email.render(context)
            if self.reply_address:
                template_reply_to = Template(self.reply_address)
                message_args['reply_to'] = template_reply_to.render(context)
            else:
                template_reply_to = Template(settings.EMAIL_ADDR)
                message_args['reply_to'] = template_reply_to.render(context)

            mail.send(
                address,
                message_args['from_email'],
                subject=message_args['subject'],
                message='\n-------------------- \n' + message_args['body'],
                headers={'Reply-to': message_args['reply_to']}
            )

    def render_landing_page(self, request, form_submission=None):

        """
        Renders the landing page.

        You can override this method to return a different HttpResponse as
        landing page. E.g. you could return a redirect to a separate page.
        """
        if self.thank_you_page:
            messages.success(request, _('Successfully submitted the form.'))
            return redirect(self.thank_you_page.url)

        context = self.get_context(request)
        context['form_submission'] = form_submission
        response = render(
            request,
            self.get_landing_page_template(request),
            context
        )
        return response

    def data_to_dict(self, processed_data, request):
        """
        Converts processed form data into a dictionary suitable
        for rendering in a context.
        """
        dictionary = {}

        for key, value in processed_data.items():
            new_key = key.replace('-', '_')
            if isinstance(value, list):
                dictionary[new_key] = ', '.join(value)
            else:
                dictionary[new_key] = utils.attempt_protected_media_value_conversion(request, value)

        return dictionary

    preview_modes = [
        ('form', _('Form')),
        ('landing', _('Thank you page')),
    ]

    def serve_preview(self, request, mode):
        if mode == 'landing':
            request.is_preview = True
            return self.render_landing_page(request)

        return super().serve_preview(request, mode)

    def serve_submissions_list_view(self, request, *args, **kwargs):
        """
        Returns list submissions view for admin.

        `list_submissions_view_class` can be set to provide custom view class.
        Your class must be inherited from SubmissionsListView.
        """
        view = self.submissions_list_view_class.as_view()
        return view(request, form_page=self, *args, **kwargs)

    def get_form(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form_params = self.get_form_parameters()
        form_params.update(kwargs)

        if request.method == 'POST':
            return form_class(request.POST, request.FILES, *args, **form_params)
        return form_class(*args, **form_params)

    def contains_spam(self, request):
        """
        Checks to see if the spam honeypot was filled out.
        """
        if request.POST.get("ws-decoy-comments", None):
            return True
        return False

    def process_spam_request(self, form, request):
        """
        Called when spam is found in the request.
        """
        messages.error(request, self.get_spam_message())
        logger.info("Detected spam submission on page: {0}\n{1}".format(self.title, vars(request)))

        return self.process_form_get(form, request)

    def get_spam_message(self):
        return _("There was an error while processing your submission.  Please try again.")

    def process_form_post(self, form, request):
        if form.is_valid():
            processed_data = self.process_data(form, request)
            form_submission = self.get_submission_class()(
                form_data=json.dumps(processed_data, cls=self.encoder),
                page=self,
            )
            self.process_form_submission(
                request=request,
                form=form,
                form_submission=form_submission,
                processed_data=processed_data)
            return self.render_landing_page(request, form_submission)
        return self.process_form_get(form, request)

    def process_form_get(self, form, request):
        context = self.get_context(request)
        context['form'] = form
        response = render(
            request,
            self.get_template(request),
            context
        )
        return response

    def serve(self, request, *args, **kwargs):
        form = self.get_form(request, page=self, user=request.user)
        if request.method == 'POST':
            if self.spam_protection and self.contains_spam(request):
                return self.process_spam_request(form, request)
            return self.process_form_post(form, request)
        return self.process_form_get(form, request)


class BasicFormPage(FormPageMixin, WebPage):
    """
    This is basically a clone of wagtail.contrib.forms.models.AbstractForm
    with changes in functionality and extending WebPage vs wagtailcore.Page.
    """
    class Meta:
        verbose_name = _('Basic Form Page')

    template = 'website/pages/form_page.html'
    landing_page_template = 'website/pages/form_page_landing.html'

    base_form_class = WagtailAdminFormPageForm

    form_builder = FormBuilder

    parent_page_types = ['website.GenericPage']

    subpage_types = []

    body_content_panels = [
        InlinePanel('form_fields', label="Form fields"),
    ] + \
        WebPage.body_content_panels + \
        FormPageMixin.body_content_panels + [
            FormSubmissionsPanel(),
            InlinePanel('confirmation_emails', label=_('Confirmation Emails'))
    ]

    settings_panels = WebPage.settings_panels + FormPageMixin.settings_panels

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not hasattr(self, 'landing_page_template'):
            name, ext = os.path.splitext(self.template)
            self.landing_page_template = name + '_landing' + ext

    def get_form_fields(self):
        """
        Form page expects `form_fields` to be declared.
        If you want to change backwards relation name,
        you need to override this method.
        """

        return self.form_fields.all()

    def get_data_fields(self):
        """
        Returns a list of tuples with (field_name, field_label).
        """

        data_fields = [
            ('submit_time', _('Submission date')),
        ]
        data_fields += [
            (field.clean_name, field.label)
            for field in self.get_form_fields()
        ]
        return data_fields

    def get_form_class(self):
        fb = self.form_builder(self.get_form_fields())
        return fb.get_form_class()

    def get_form_parameters(self):
        return {}

    def get_submission_class(self):
        """
        Returns submission class.

        You can override this method to provide custom submission class.
        Your class must be inherited from AbstractFormSubmission.
        """

        return FormSubmission


class FormSubmissionRevision(FlexibleformSubmissionRevision, models.Model):
    pass


class SessionFormSubmission(FlexibleformSessionFormSubmission):

    INCOMPLETE = 'incomplete'
    COMPLETE = 'complete'
    REVIEWED = 'reviewed'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    STATUSES = (
        (INCOMPLETE, _('Not submitted')),
        (COMPLETE, _('Complete')),
        (REVIEWED, _('Under consideration')),
        (APPROVED, _('Approved')),
        (REJECTED, _('Rejected')),
    )
    status = models.CharField(max_length=10, choices=STATUSES, default=INCOMPLETE)

    def create_normal_submission(self, delete_self=True):
        submission_data = self.get_data()
        if 'user' in submission_data:
            submission_data['user'] = str(submission_data['user'])
        submission = FormSubmission.objects.create(
            form_data=json.dumps(submission_data, cls=StreamFormJSONEncoder),
            page=self.page
        )

        if delete_self:
            FormSubmissionRevision.objects.filter(submission_id=self.id).delete()
            self.delete()

        return submission

    def render_email(self, value):
        return value

    def render_link(self, value):
        return "{0}{1}".format(page_choices['PROTECTED_MEDIA_URL'], value)

    def render_image(self, value):
        return "{0}{1}".format(page_choices['PROTECTED_MEDIA_URL'], value)

    def render_file(self, value):
        return "{0}{1}".format(page_choices['PROTECTED_MEDIA_URL'], value)


@receiver(post_save)
def create_submission_changed_revision(sender, **kwargs):
    if not issubclass(sender, SessionFormSubmission):
        return
    submission = kwargs['instance']
    created = kwargs['created']
    FormSubmissionRevision.create_from_submission(
        submission, (FormSubmissionRevision.CREATED if created else FormSubmissionRevision.CHANGED))  # noqa


@receiver(post_delete)
def create_submission_deleted_revision(sender, **kwargs):
    if not issubclass(sender, SessionFormSubmission):
        return
    submission = kwargs['instance']
    FormSubmissionRevision.create_from_submission(submission, FlexibleformSubmissionRevision.DELETED)  # noqa


class FormStep(Step):

    def get_markups_and_bound_fields(self, form):
        for struct_child in self.form_fields:
            block = struct_child.block
            if isinstance(block, FormFieldBlock):
                struct_value = struct_child.value
                field_name = block.get_slug(struct_value)
                yield form[field_name], 'field', struct_child
            else:
                yield mark_safe(struct_child), 'markup'


class FormSteps(Steps):

    def __init__(self, page, request=None):
        self.page = page
        # TODO: Make it possible to change the `form_fields` attribute.
        self.form_fields = page.form_fields
        self.request = request
        has_steps = any(isinstance(struct_child.block, FormStepBlock)
                        for struct_child in self.form_fields)
        if has_steps:
            steps = [FormStep(self, i, form_field)
                     for i, form_field in enumerate(self.form_fields)]
        else:
            steps = [FormStep(self, 0, self.form_fields)]
        super(Steps, self).__init__(steps)


class StreamFormMixin(FlexibleformStreamFormMixin):

    def get_steps(self, request=None):
        if not hasattr(self, 'steps'):
            steps = FormSteps(self, request=request)
            if request is None:
                return steps
            self.steps = steps
        return self.steps

    @staticmethod
    def get_submission_class():
        return FormSubmission

    @staticmethod
    def get_session_submission_class():
        return SessionFormSubmission

    def get_submission(self, request):
        Submission = self.get_session_submission_class()
        if request.user.is_authenticated:
            user_submission = Submission.objects.filter(
                user=request.user, page=self).order_by('-pk').first()
            if user_submission is None:
                return Submission(user=request.user, page=self, form_data='[]')
            return user_submission

        # Custom code to ensure that anonymous users get a session key.
        if not request.session.session_key:
            request.session.create()

        user_submission = Submission.objects.filter(
            session_key=request.session.session_key, page=self
        ).order_by('-pk').first()
        if user_submission is None:
            return Submission(session_key=request.session.session_key,
                              page=self, form_data='[]')
        return user_submission


class StreamFormPage(FormPageMixin, StreamFormMixin, WebPage):
    class Meta:
        verbose_name = _('Complex Form Page')

    template = 'website/pages/stream_form_page.html'
    landing_page_template = 'website/pages/form_page_landing.html'

    form_fields = StreamField(streamform_blocks)
    encoder = StreamFormJSONEncoder

    parent_page_types = ['website.GenericPage']

    subpage_types = []

    body_content_panels = [
        StreamFieldPanel('form_fields')
    ] + \
        FormPageMixin.body_content_panels + [
            InlinePanel('confirmation_emails', label=_('Confirmation Emails'))
    ]

    def process_form_post(self, form, request):
        if form.is_valid():
            is_complete = self.steps.update_data()
            if is_complete:
                submission = self.get_submission(request)
                self.process_form_submission(
                    request=request,
                    form=form,
                    form_submission=submission,
                    processed_data=submission.get_data()
                )
                normal_submission = submission.create_normal_submission()
                return self.render_landing_page(request, normal_submission)
            return HttpResponseRedirect(self.url)
        return self.process_form_get(form, request)

    def process_form_get(self, form, request):
        return WebPage.serve(self, request)

    def get_form(self, request, *args, **kwargs):
        return self.get_context(request)['form']

    def get_storage(self):
        return FileSystemStorage(
            location=page_choices['PROTECTED_MEDIA_ROOT'],
            base_url=page_choices['PROTECTED_MEDIA_URL']
        )