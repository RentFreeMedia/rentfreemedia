from django.db import models
from django.utils.translation import ugettext_lazy as _
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    StreamFieldPanel
)
from wagtail.core.fields import StreamField
from wagtail.core.models import Orderable
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.snippets.models import register_snippet
from website.models.blocks import html_streamblocks, layout_streamblocks, contentwall_streamblocks
from website.models.choices import page_choices


@register_snippet
class Carousel(ClusterableModel):
    """
    Model that represents a Carousel. Can be modified through the snippets UI.
    Selected through Page StreamField bodies by the CarouselSnippetChooser in
    snippet_choosers.py
    """
    class Meta:
        verbose_name = _('Carousel')

    name = models.CharField(
        max_length=255,
        verbose_name=_('Name'),
    )
    show_controls = models.BooleanField(
        default=True,
        verbose_name=_('Show controls'),
        help_text=_('Shows arrows on the left and right of the carousel to advance next or previous slides.'),  # noqa
    )
    show_indicators = models.BooleanField(
        default=True,
        verbose_name=_('Show indicators'),
        help_text=_('Shows small indicators at the bottom of the carousel based on the number of slides.'),  # noqa
    )
    animation = models.CharField(
        blank=True,
        max_length=20,
        choices=page_choices['CAROUSEL_FX_CHOICES'],
        default=page_choices['CAROUSEL_FX_DEFAULT'],
        verbose_name=_('Animation'),
        help_text=_('The animation when transitioning between slides.'),
    )

    panels = (
        [
            MultiFieldPanel(
                heading=_('Slider'),
                children=[
                    FieldPanel('name'),
                    FieldPanel('show_controls'),
                    FieldPanel('show_indicators'),
                    FieldPanel('animation'),
                ]
            ),
            InlinePanel('carousel_slides', label=_('Slides'))
        ]
    )

    def __str__(self):
        return self.name


class CarouselSlide(Orderable, models.Model):
    """
    Represents a slide for the Carousel model. Can be modified through the
    snippets UI.
    """
    class Meta:
        verbose_name = _('Carousel Slide')

    carousel = ParentalKey(
        Carousel,
        related_name='carousel_slides',
        verbose_name=_('Carousel'),
    )
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_('Image'),
    )
    background_color = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Background color'),
        help_text=_('Hexadecimal, rgba, or CSS color notation (e.g. #ff0011)'),
    )
    custom_css_class = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Custom CSS class'),
    )
    custom_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Custom ID'),
    )

    content = StreamField(html_streamblocks, blank=True)

    panels = (
        [
            ImageChooserPanel('image'),
            FieldPanel('background_color'),
            FieldPanel('custom_css_class'),
            FieldPanel('custom_id'),
            StreamFieldPanel('content'),
        ]
    )


@register_snippet
class Header(models.Model):

    class Meta:
        verbose_name = _('Header')
        verbose_name_plural = _('Headers')

    name = models.CharField(
        max_length=255,
        verbose_name=_('Name'),
    )
    custom_css_class = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('CSS Class(es)'),
        help_text=_('Optional, free-form, spaced list of custom css classes. Ex: "max-w-max bg-gray"')
    )
    custom_id = models.CharField(
        blank=True,
        max_length=255,
        verbose_name=_('CSS ID'),
        help_text=_('Optional, CSS ID to identify the wrapper element.')
    )
    content = StreamField(
        layout_streamblocks,
        verbose_name=_('Content'),
    )

    panels = [
        FieldPanel('name'),
        MultiFieldPanel(
            [
                FieldPanel('custom_css_class'),
                FieldPanel('custom_id'),
            ],
            heading=_('Attributes')
        ),
        StreamFieldPanel('content')
    ]

    def __str__(self):
        return self.name


@register_snippet
class Footer(models.Model):

    class Meta:
        verbose_name = _('Footer')
        verbose_name_plural = _('Footers')

    name = models.CharField(
        max_length=255,
        verbose_name=_('Name'),
    )
    custom_css_class = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('CSS Class(es)'),
        help_text=_('Optional, free-form, spaced list of custom css classes. Ex: "max-w-max bg-gray"')
    )
    custom_id = models.CharField(
        blank=True,
        max_length=255,
        verbose_name=_('CSS ID'),
        help_text=_('Optional, CSS ID to identify the wrapper element.')
    )
    content = StreamField(
        layout_streamblocks,
        verbose_name=_('Content'),
    )

    panels = [
        FieldPanel('name'),
        MultiFieldPanel(
            [
                FieldPanel('custom_css_class'),
                FieldPanel('custom_id'),
            ],
            heading=_('Attributes')
        ),
        StreamFieldPanel('content')
    ]

    def __str__(self):
        return self.name


@register_snippet
class ReusableContent(models.Model):
    """
    Snippet for resusable content in streamfields.
    """
    class Meta:
        verbose_name = _('Reusable Content')
        verbose_name_plural = _('Reusable Content')

    name = models.CharField(
        max_length=255,
        verbose_name=_('Name'),
    )
    content = StreamField(
        layout_streamblocks,
        verbose_name=_('content')
    )

    panels = [
        FieldPanel('name'),
        StreamFieldPanel('content')
    ]

    def __str__(self):
        return self.name


@register_snippet
class ContentWall(models.Model):
    """
    Snippet that restricts access to a page with a modal.
    """
    class Meta:
        verbose_name = _('Content Wall')

    name = models.CharField(
        max_length=255,
        verbose_name=_('Name'),
    )
    content = StreamField(
        contentwall_streamblocks,
        verbose_name=_('Content'),
    )
    is_dismissible = models.BooleanField(
        default=True,
        verbose_name=_('Dismissible'),
    )
    show_once = models.BooleanField(
        default=True,
        verbose_name=_('Show once'),
        help_text=_('Do not show the content wall to the same user again after it has been closed.')
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel('name'),
                FieldPanel('is_dismissible'),
                FieldPanel('show_once'),
            ],
            heading=_('Content Wall')
        ),
        StreamFieldPanel('content'),
    ]

    def __str__(self):
        return self.name


class Email(ClusterableModel):
    """
    General purpose abstract clusterable model used for holding email information.
    Most likely this should be subclassed with addition of a ParentalKey.
    """
    class Meta:
        abstract = True
        verbose_name = _('Email')

    to_address = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('To Addresses'),
        help_text=_('Separate multiple email addresses with commas.')
    )
    from_address = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('From Address'),
        help_text=_('For example: "sender@example.com" or "Sender Name <sender@example.com>" (without quotes).')  # noqa
    )
    reply_address = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Reply-To Address'),
        help_text=_('Separate multiple email addresses with commas.')
    )
    cc_address = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('CC'),
        help_text=_('Separate multiple email addresses with commas.')
    )
    bcc_address = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('BCC'),
        help_text=_('Separate multiple email addresses with commas.')
    )
    subject = models.CharField(max_length=255, blank=True, verbose_name=_('Subject'))
    body = models.TextField(blank=True, verbose_name=_('Body'))

    panels = (
        [
            MultiFieldPanel(
                [
                    FieldPanel('to_address'),
                    FieldPanel('from_address'),
                    FieldPanel('cc_address'),
                    FieldPanel('bcc_address'),
                    FieldPanel('subject'),
                    FieldPanel('body'),
                ],
                _('Email Message')
            ),
        ])

    def __str__(self):
        return self.subject
