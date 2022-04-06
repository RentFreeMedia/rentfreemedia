import json
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from post_office.validators import validate_email_with_name
from wagtail.admin.edit_handlers import HelpPanel, FieldPanel, MultiFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.contrib.settings.models import BaseSetting, register_setting
from website import schema
from website.models.choices import page_choices
from wagtail.admin.edit_handlers import PageChooserPanel
from wagtail.snippets.edit_handlers import SnippetChooserPanel


@register_setting(icon='order')
class LayoutSettings(BaseSetting):
    """
    Branding settings.
    """
    class Meta:
        verbose_name = _('Layout')

    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_('Logo'),
        help_text=_('Brand logo used throughout the site')
    )
    favicon = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='favicon',
        verbose_name=_('Favicon'),
    )
    show_search_images = models.BooleanField(
        null=False,
        blank=False,
        default=True,
        choices=page_choices['BOOLEAN_CHOICES'],
        verbose_name=_('Search images'),
        help_text=_('Show page cover images on search results list?'),
    )
    show_search_captions = models.BooleanField(
        null=False,
        blank=False,
        default=True,
        choices=page_choices['BOOLEAN_CHOICES'],
        verbose_name=_('Search captions'),
        help_text=_('Show page captions on search results list?'),
    )
    show_search_meta = models.BooleanField(
        null=False,
        blank=False,
        default=True,
        choices=page_choices['BOOLEAN_CHOICES'],
        verbose_name=_('Search meta'),
        help_text=_('Show page metadata, like the date, in search results list?'),
    )
    show_search_preview = models.BooleanField(
        null=False,
        blank=False,
        default=True,
        choices=page_choices['BOOLEAN_CHOICES'],
        verbose_name=_('Search previews'),
        help_text=_('Show page body preview text on search results list?'),
    )
    search_header = models.ForeignKey(
        'website.Header',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Search Header / Navbar'
    )
    search_footer = models.ForeignKey(
        'website.Footer',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Search Footer'
    )
    subscribe_header = models.ForeignKey(
        'website.Header',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Subscribe Header / Navbar'
    )
    subscribe_footer = models.ForeignKey(
        'website.Footer',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='Subscribe Footer'
    )
    account_header = models.ForeignKey(
        'website.Header',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='User Profile Header / Navbar'
    )
    account_footer = models.ForeignKey(
        'website.Footer',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name='User Profile Footer'
    )

    panels = [
        MultiFieldPanel(
            [
                ImageChooserPanel('logo'),
                ImageChooserPanel('favicon'),
            ],
            heading=_('Sitewide images'),
            help_text=_('Default images, logo can be overriden by page-level alternatives')
        ),
        MultiFieldPanel(
            [
                FieldPanel('show_search_images'),
                FieldPanel('show_search_captions'),
                FieldPanel('show_search_meta'),
                FieldPanel('show_search_preview'),
            ],
            heading=_('Search result page options'),
            help_text=_('Sitewide search page output choices, you probably want to match your index page preferences.')
        ),
        MultiFieldPanel(
            [
                SnippetChooserPanel('search_header'),
                SnippetChooserPanel('search_footer'),
            ],
            heading=_('Search page header / footer'),
            help_text=_('Header and footer for all search result pages')
        ),
        MultiFieldPanel(
            [
                SnippetChooserPanel('subscribe_header'),
                SnippetChooserPanel('subscribe_footer'),
            ],
            heading=_('Subscribe page header / footer'),
            help_text=_('Header and footer for all subscription action pages')
        ),
        MultiFieldPanel(
            [
                SnippetChooserPanel('account_header'),
                SnippetChooserPanel('account_footer'),
            ],
            heading=_('User profile page header / footer'),
            help_text=_('Header and footer for all user profile, registration, and login / logout pages')
        ),
    ]


@register_setting(icon='group')
class SocialMediaSettings(BaseSetting):
    """
    Social media accounts.
    """
    class Meta:
        verbose_name = _('Social Media')

    apple_podcasts = models.URLField(
        blank=True,
        verbose_name=_('Apple Podcasts'),
        help_text=_('Your Apple Podcasts URL')
    )
    google_podcasts = models.URLField(
        blank=True,
        verbose_name=_('Google Podcasts'),
        help_text=_('Your Google Podcasts URL')
    )
    spotify = models.URLField(
        blank=True,
        verbose_name=_('Spotify'),
        help_text=_('Your Spotify podcast URL')
    )
    stitcher = models.URLField(
        blank=True,
        verbose_name=_('Stitcher'),
        help_text=_('Your Stitcher podcast URL')
    )
    facebook = models.URLField(
        blank=True,
        verbose_name=_('Facebook'),
        help_text=_('Your Facebook page URL'),
    )
    twitter = models.URLField(
        blank=True,
        verbose_name=_('Twitter'),
        help_text=_('Your Twitter page URL'),
    )
    instagram = models.URLField(
        blank=True,
        verbose_name=_('Instagram'),
        help_text=_('Your Instagram page URL'),
    )
    tiktok = models.URLField(
        blank=True,
        verbose_name=_('TikTok'),
        help_text=_('Your TikTok URL'),
    )
    reddit = models.URLField(
        blank=True,
        verbose_name=_('Reddit'),
        help_text=_('Your subreddit URL'),
    )
    snapchat = models.URLField(
        blank=True,
        verbose_name=_('Snapchat'),
        help_text=_('Your Snapchat URL'),
    )
    wikipedia = models.URLField(
        blank=True,
        verbose_name=_('Wikipedia'),
        help_text=_('Your Wikipedia URL'),
    )
    youtube = models.URLField(
        blank=True,
        verbose_name=_('YouTube'),
        help_text=_('Your YouTube channel or user account URL'),
    )
    linkedin = models.URLField(
        blank=True,
        verbose_name=_('LinkedIn'),
        help_text=_('Your LinkedIn page URL'),
    )
    google = models.URLField(
        blank=True,
        verbose_name=_('Google'),
        help_text=_('Your Google business listing URL'),
    )

    @property
    def twitter_handle(self):
        """
        Gets the handle of the twitter account from a URL.
        """
        return self.twitter.strip().strip('/').split('/')[-1]

    @property
    def social_json(self):
        """
        Returns non-blank social accounts as a JSON list.
        """
        socialist = [
            self.apple_podcasts,
            self.google_podcasts,
            self.spotify,
            self.stitcher,
            self.facebook,
            self.twitter,
            self.instagram,
            self.tiktok,
            self.reddit,
            self.snapchat,
            self.wikipedia,
            self.youtube,
            self.linkedin,
            self.google,
        ]
        socialist = list(filter(None, socialist))
        if socialist:
            return json.dumps(socialist)
        else:
            return None

    @property
    def social_dict(self):
        """
        Returns non-blank social accounts as dict, empty string if None for error avoidance in snippets.
        """
        socialist = {
                "apple_podcasts": self.apple_podcasts if self.apple_podcasts else '',
                "google_podcasts": self.google_podcasts if self.google_podcasts else '',
                "spotify": self.spotify if self.spotify else '',
                "stitcher": self.stitcher if self.stitcher else '',
                "facebook": self.facebook if self.facebook else '',
                "twitter": self.twitter if self.twitter else '',
                "instagram": self.instagram if self.instagram else '',
                "tiktok": self.tiktok if self.tiktok else '',
                "reddit": self.reddit if self.reddit else '',
                "snapchat": self.snapchat if self.snapchat else '',
                "wikipedia": self.wikipedia if self.wikipedia else '',
                "youtube": self.youtube if self.youtube else '',
                "linkedin": self.linkedin if self.linkedin else '',
                "google": self.google if self.google else ''
            }

        return socialist

    panels = [
        MultiFieldPanel(
            [
                FieldPanel('apple_podcasts'),
                FieldPanel('google_podcasts'),
                FieldPanel('spotify'),
                FieldPanel('stitcher'),
                FieldPanel('facebook'),
                FieldPanel('twitter'),
                FieldPanel('instagram'),
                FieldPanel('tiktok'),
                FieldPanel('reddit'),
                FieldPanel('snapchat'),
                FieldPanel('wikipedia'),
                FieldPanel('youtube'),
                FieldPanel('linkedin'),
                FieldPanel('google'),
            ],
            _('Social Media Accounts'),
        )
    ]


@register_setting(icon='view')
class AnalyticsSettings(BaseSetting):
    """
    Tracking and Google Analytics.
    """
    class Meta:
        verbose_name = _('Tracking')

    ga_tracking_id = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        verbose_name=_('GA Tracking ID'),
        help_text=_('Your Google Analytics tracking ID (begins with "UA- or G-")'),
    )
    ga_tag_manager_id = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        verbose_name=_('Google Tag Manager ID'),
        help_text=_('Your Google Tag Manager ID if you wish to track clicks.'),
    )
    ga_track_button_clicks = models.BooleanField(
        default=False,
        verbose_name=_('Track button clicks'),
        help_text=_('Track all button clicks using Google Analytics event tracking. Event tracking details can be specified in each button’s advanced settings options.'),  # noqa
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel('ga_tracking_id'),
                FieldPanel('ga_tag_manager_id'),
                FieldPanel('ga_track_button_clicks'),
            ],
            heading=_('Google Analytics')
        )
    ]


@register_setting(icon='cog')
class GeneralSettings(BaseSetting):

    from_email = models.CharField(
        default=settings.EMAIL_ADDR,
        max_length=255,
        verbose_name=_('From email'),
        validators=[validate_email_with_name],
        help_text=_('The default email address this site sends from, may include name, ex: "Admin <admin@admin.com>"'),  # noqa
    )
    search_num_results = models.PositiveIntegerField(
        default=10,
        verbose_name=_('Results per page'),
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel('from_email'),
            ],
            _('Email')
        ),
        MultiFieldPanel(
            [
                FieldPanel('search_num_results'),
            ],
            _('Search Settings')
        ),
    ]

    class Meta:
        verbose_name = _('General')


@register_setting(icon='tag')
class SeoSettings(BaseSetting):
    """
    Additional search engine optimization and meta tags
    that can be turned on or off.
    """
    class Meta:
        verbose_name = _('SEO')

    main_entity_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_('Main Entity Page'),
        help_text=_('Choose a page that represents the main content of the site to have it included in search engine markup.')
    )
    og_meta = models.BooleanField(
        default=True,
        verbose_name=_('Use OpenGraph Markup'),
        help_text=_('Show an optimized preview when linking to this site on Facebook, Linkedin, Twitter, and others. See http://ogp.me/.'),  # noqa
    )
    twitter_meta = models.BooleanField(
        default=True,
        verbose_name=_('Use Twitter Markup'),
        help_text=_('Shows content as a "card" when linking to this site on Twitter. See https://developer.twitter.com/en/docs/tweets/optimize-with-cards/overview/abouts-cards.'),  # noqa
    )
    struct_meta = models.BooleanField(
        default=True,
        verbose_name=_('Use Structured Data'),
        help_text=_('Optimizes information about your organization for search engines. See https://schema.org/.'),  # noqa
    )
    struct_org_type = models.CharField(
        default='',
        blank=True,
        max_length=255,
        choices=schema.SCHEMA_ORG_TYPES,
        verbose_name=_('Organization type'),
        help_text=_('If blank, no structured data will be used on this page.')
    )
    struct_org_contenttype = models.CharField(
        default='',
        blank=True,
        max_length=255,
        choices=schema.SCHEMA_CONTENT_CHOICES,
        verbose_name=_('Content Type'),
        help_text=_('Default type of thing (article, podcast episode, etc.)')
    )
    struct_org_name = models.CharField(
        default='',
        blank=True,
        max_length=255,
        verbose_name=_('Organization name'),
        help_text=_('Leave blank to use the site name in Settings > Sites')
    )
    struct_org_logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_('Organization logo'),
        help_text=_('Leave blank to use the logo in Settings > Layout > Logo')
    )
    struct_org_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_('Photo of Organization'),
        help_text=_('A photo of the facility. This photo will be cropped to 1:1, 4:3, and 16:9 aspect ratios automatically.'),  # noqa
    )
    struct_org_phone = models.CharField(
        blank=True,
        max_length=255,
        verbose_name=_('Telephone number'),
        help_text=_('Include country code for best results. For example: +1-216-555-8000')
    )
    struct_org_address_street = models.CharField(
        blank=True,
        max_length=255,
        verbose_name=_('Street address'),
        help_text=_('House number and street. For example, 55 Public Square Suite 1710')
    )
    struct_org_address_locality = models.CharField(
        blank=True,
        max_length=255,
        verbose_name=_('City'),
        help_text=_('City or locality. For example, Cleveland')
    )
    struct_org_address_region = models.CharField(
        blank=True,
        max_length=255,
        verbose_name=_('State'),
        help_text=_('State, province, county, or region. For example, OH')
    )
    struct_org_address_postal = models.CharField(
        blank=True,
        max_length=255,
        verbose_name=_('Postal code'),
        help_text=_('Zip or postal code. For example, 44113')
    )
    struct_org_address_country = models.CharField(
        blank=True,
        max_length=255,
        verbose_name=_('Country'),
        help_text=_('For example, USA. Two-letter ISO 3166-1 alpha-2 country code is also acceptible https://en.wikipedia.org/wiki/ISO_3166-1'),  # noqa
    )
    struct_org_geo_lat = models.DecimalField(
        blank=True,
        null=True,
        max_digits=10,
        decimal_places=8,
        verbose_name=_('Geographic latitude')
    )
    struct_org_geo_lng = models.DecimalField(
        blank=True,
        null=True,
        max_digits=10,
        decimal_places=8,
        verbose_name=_('Geographic longitude')
    )
    struct_org_extra_json = models.TextField(
        blank=True,
        verbose_name=_('Additional Organization markup'),
        help_text=_('Additional JSON-LD inserted into the Organization dictionary. Must be properties of https://schema.org/Organization or the selected organization type.'),  # noqa
    )

    panels = [
        MultiFieldPanel(
            [
                ImageChooserPanel('struct_org_image'),
                FieldPanel('struct_org_phone'),
                FieldPanel('struct_org_address_street'),
                FieldPanel('struct_org_address_locality'),
                FieldPanel('struct_org_address_region'),
                FieldPanel('struct_org_address_postal'),
                FieldPanel('struct_org_address_country'),
                FieldPanel('struct_org_geo_lat'),
                FieldPanel('struct_org_geo_lng'),
                HelpPanel(content=_('Optional local business metadata. If these settings are enabled, the corresponding values in each page’s SEO output are used.')),  # noqa
            ],
            heading=_('Optional Local Search Metadata'),
            classname='collapsible collapsed'
        ),
        MultiFieldPanel(
            [
                PageChooserPanel('main_entity_page', ['website.PodcastContentIndexPage', 'website.ArticleContentIndexPage']),
                FieldPanel('og_meta'),
                FieldPanel('twitter_meta'),
                FieldPanel('struct_meta'),
                FieldPanel('struct_org_type'),
                FieldPanel('struct_org_contenttype'),
                FieldPanel('struct_org_name'),
                ImageChooserPanel('struct_org_logo'),
                FieldPanel('struct_org_extra_json'),
                HelpPanel(content=_('If these settings are enabled, the corresponding values in each page’s SEO output are used.')),  # noqa
            ],
            heading=_('Search Metadata')
        )
    ]


@register_setting(icon='cogs')
class GoogleApiSettings(BaseSetting):
    """
    Settings for Google API services.
    """
    class Meta:
        verbose_name = _('Google API')

    google_maps_api_key = models.CharField(
        blank=True,
        max_length=255,
        verbose_name=_('Google Maps API Key'),
        help_text=_('The API Key used for Google Maps.')
    )
