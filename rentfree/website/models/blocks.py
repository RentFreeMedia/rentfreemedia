"""
Bases, mixins, and utilites for blocks.
"""
import logging
from django import forms
from django.template.loader import render_to_string
from django.utils.encoding import force_text
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from wagtail.core import blocks
from wagtail.core.models import Collection, Site
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtailmarkdown.blocks import MarkdownBlock
from website.models.choices import page_choices
from website.wagtail_flexible_forms import blocks as FlexibleformBlocks
from website.forms import (
    DateField, 
    DateInput,
    DateTimeField, 
    DateTimeInput,
    TimeField, 
    TimeInput
)


logger = logging.getLogger('website')


class OptionalSettings(blocks.StructBlock):
    """
    Common fields each block should have,
    which are hidden under the block's "Advanced Settings" dropdown.
    """
    # placeholder, real value get set in __init__()
    custom_template = blocks.Block()

    custom_css_class = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_('Custom CSS Class'),
    )
    custom_id = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_('Custom ID'),
    )

    class Meta:
        form_template = 'wagtailadmin/block_forms/base_block_settings_struct.html'
        label = _(' ')

    def __init__(self, local_blocks=None, template_choices=None, **kwargs):
        if not local_blocks:
            local_blocks = ()

        local_blocks += (
            (
                'custom_template',
                blocks.ChoiceBlock(
                    choices=template_choices,
                    default=None,
                    required=False,
                    label=_('Template'))
            ),
        )

        super().__init__(local_blocks, **kwargs)


class OptionalTrackingSettings(OptionalSettings):
    """
    OptionalSettings plus additional tracking fields.
    """
    ga_tracking_event_category = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_('Tracking Event Category'),
    )
    ga_tracking_event_label = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_('Tracking Event Label'),
    )


class OptionalColumnSettings(OptionalSettings):
    """
    BaseBlockSettings plus additional column fields.
    """
    column_breakpoint = blocks.ChoiceBlock(
        choices=page_choices['COL_BREAK_CHOICES'],
        default=page_choices['COL_BREAK_DEFAULT'],
        required=False,
        verbose_name=_('Column Breakpoint'),
        help_text=_('Screen size at which the column will expand horizontally or stack vertically.'),
    )


class OptionalColumnSettingsCards(OptionalSettings):
    """
    BaseBlockSettings plus additional column fields for card deck.
    """
    column_breakpoint = blocks.ChoiceBlock(
        choices=page_choices['COL_BREAK_CHOICES'],
        default=page_choices['COL_BREAK_DEFAULT'],
        required=False,
        verbose_name=_('Column Breakpoint'),
        help_text=_('Screen size at which the column will expand horizontally or stack vertically.'),
    )
    column_size = blocks.ChoiceBlock(
        choices=page_choices['COL_SIZE_CHOICES'],
        default=page_choices['COL_SIZE_DEFAULT'],
        required=False,
        label=_('Column size'),
    )


class OptionalEmbedSettings(OptionalSettings):
    """
    BaseBlockSettings plus additional column fields for card deck.
    """
    max_width = blocks.ChoiceBlock(
        choices=page_choices['EMBED_WIDTH_CHOICES'],
        default=page_choices['EMBED_WIDTH_DEFAULT'],
        required=False,
        verbose_name=_('Column Breakpoint'),
        help_text=_('Screen size at which the column will expand horizontally or stack vertically.'),
    )


class OptionalFormSettings(OptionalSettings):

    condition_trigger_id = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_('Condition Trigger ID'),
        help_text=_(
            'The "Custom ID" of another field that that will trigger this field to be shown/hidden.')  # noqa
    )
    condition_trigger_value = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_('Condition Trigger Value'),
        help_text=_(
            'The value of the field in "Condition Trigger ID" that will trigger this field to be shown.')  # noqa
    )

class OptionalButtonSettings(OptionalSettings):
    """
    OptionalSettings plus additional tracking fields and icon fields.
    """
    button_icon = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_('Icon Class'),
    )
    icon_size = blocks.IntegerBlock(
        max_length=255,
        required=False,
        label=_('Icon Size'),
        help_text=_('Icon size in pixels')
    )
    icon_color = blocks.ChoiceBlock(
        required=False,
        choices=page_choices['BUTTON_ICON_COLOR_CHOICES'],
        help_text=_('Icon color'),
    )
    ga_tracking_event_category = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_('Tracking Event Category'),
    )
    ga_tracking_event_label = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_('Tracking Event Label'),
    )


class OptionalImagelinkSettings(OptionalSettings):
    """
    OptionalSettings plus additional tracking fields and icon fields.
    """
    fluid_image = blocks.ChoiceBlock(
        required=False,
        choices=page_choices['BOOLEAN_CHOICES'],
        label=_('Fluid Image'),
        help_text=_("Should image change size depending on the user's screen size?"),
    )
    ga_tracking_event_category = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_('Tracking Event Category'),
    )
    ga_tracking_event_label = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_('Tracking Event Label'),
    )


class LinkStructValue(blocks.StructValue):
    """
    Generates a URL for blocks with multiple link choices.
    """

    @property
    def url(self):
        page = self.get('page_link')
        doc = self.get('doc_link')
        ext = self.get('other_link')
        if page:
            return page.url
        elif doc:
            return doc.url
        elif ext:
            return ext
        elif social:
            return social


class ButtonMixin(blocks.StructBlock):
    """
    Standard style and size options for buttons.
    """
    button_title = blocks.CharBlock(
        max_length=255,
        required=False,
        label=_('Button Title'),
    )
    button_style = blocks.ChoiceBlock(
        choices=page_choices['BUTTON_STYLE_CHOICES'],
        default=page_choices['BUTTON_STYLE_DEFAULT'],
        required=False,
        label=_('Button Style'),
    )
    button_size = blocks.ChoiceBlock(
        choices=page_choices['BUTTON_SIZE_CHOICES'],
        default=page_choices['BUTTON_SIZE_DEFAULT'],
        required=False,
        label=_('Button Size'),
    )


class BaseBlock(blocks.StructBlock):

    settings_class = OptionalSettings

    settings = blocks.Block()

    def __init__(self, local_blocks=None, **kwargs):

        klassname = self.__class__.__name__.lower()
        choices = page_choices['TEMPLATES_BLOCKS'].get('*', ()) + \
            page_choices['TEMPLATES_BLOCKS'].get(klassname, ())

        if not local_blocks:
            local_blocks = ()

        local_blocks += (('settings', self.settings_class(template_choices=choices)),)

        super().__init__(local_blocks, **kwargs)

    def render(self, value, context=None):
        template = value['settings']['custom_template']

        if not template:
            template = self.get_template(context=context)
            if not template:
                return self.render_basic(value, context=context)

        if context is None:
            new_context = self.get_context(value)
        else:
            new_context = self.get_context(value, parent_context=dict(context))

        return mark_safe(render_to_string(template, new_context))


class BaseLinkBlock(BaseBlock):
    """
    Common attributes for creating a link within the CMS.
    """
    page_link = blocks.PageChooserBlock(
        required=False,
        label=_('Page link'),
    )
    doc_link = DocumentChooserBlock(
        required=False,
        label=_('Document link'),
    )
    social_link = blocks.ChoiceBlock(
        choices=page_choices['SOCIAL_LINK_CHOICES'],
        required=False,
        label=_('Social link'),
        help_text=_('Use a social media link from your site-wide settings.')
    )
    other_link = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_('Other link'),
    )

    settings_class = OptionalTrackingSettings

    class Meta:
        value_class = LinkStructValue

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)

        if value['social_link']:
            social = value['social_link']
            social_url = context['settings'].request_or_site.socialmediasettings.social_dict[social]
            context['self']['url'] = social_url

        return context


class BaseButtonBlock(BaseBlock):
    """
    Common attributes for creating a button link within the CMS.
    """
    page_link = blocks.PageChooserBlock(
        required=False,
        label=_('Page link'),
    )
    doc_link = DocumentChooserBlock(
        required=False,
        label=_('Document link'),
    )
    social_link = blocks.ChoiceBlock(
        choices=page_choices['SOCIAL_LINK_CHOICES'],
        required=False,
        label=_('Social link'),
        help_text=_('Use a social media link from your site-wide settings.')
    )
    other_link = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_('Other link'),
    )
    
    settings_class = OptionalButtonSettings

    class Meta:
        value_class = LinkStructValue

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)

        if value['social_link']:
            social = value['social_link']
            social_url = context['settings'].request_or_site.socialmediasettings.social_dict[social]
            context['self']['url'] = social_url
            
        return context


class BaseImagelinkBlock(BaseBlock):
    """
    Common attributes for creating a link within the CMS.
    """
    page_link = blocks.PageChooserBlock(
        required=False,
        label=_('Page link'),
    )
    doc_link = DocumentChooserBlock(
        required=False,
        label=_('Document link'),
    )
    social_link = blocks.ChoiceBlock(
        choices=page_choices['SOCIAL_LINK_CHOICES'],
        required=False,
        label=_('Social link'),
        help_text=_('Use a social media link from your site-wide settings.')
    )
    other_link = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_('Other link'),
    )
    
    settings_class = OptionalImagelinkSettings

    class Meta:
        value_class = LinkStructValue

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)

        if value['social_link']:
            social = value['social_link']
            social_url = context['settings'].request_or_site.socialmediasettings.social_dict[social]
            context['self']['url'] = social_url
        
        return context


class ButtonBlock(ButtonMixin, BaseButtonBlock):
    """
    A link styled as a button.
    """
    class Meta:
        template = 'website/blocks/button_block.html'
        icon = 'placeholder'
        label = _('Button Link')
        value_class = LinkStructValue


class DownloadBlock(ButtonMixin, BaseBlock):
    """
    Link to a file that can be downloaded.
    """
    downloadable_file = DocumentChooserBlock(
        required=False,
        label=_('Document link'),
    )

    settings_class = OptionalTrackingSettings

    class Meta:
        template = 'website/blocks/download_block.html'
        icon = 'download'
        label = _('Download')


class EmbedGoogleMapBlock(BaseBlock):
    """
    An embedded Google map in an <iframe>.
    """
    search = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_('Search query'),
        help_text=_('Address or search term used to find your location on the map.'),
    )
    place_id = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_('Google place ID'),
        help_text=_('Requires API key to use place ID.')
    )
    map_zoom_level = blocks.IntegerBlock(
        required=False,
        default=14,
        label=_('Map zoom level'),
        help_text=_(
            "Requires API key to use zoom. 1: World, 5: Landmass/continent, 10: City, 15: Streets, 20: Buildings"  # noqa
        )
    )

    class Meta:
        template = 'website/blocks/google_map.html'
        icon = 'site'
        label = _('Google Map')


class EmbedBlock(BaseBlock):
    """
    Emedded media using stock wagtail functionality.
    """
    url = blocks.URLBlock(
        label=_('URL'),
        help_text=_('Link to a YouTube/Vimeo video, tweet, etc.')
    )

    settings_class = OptionalEmbedSettings

    class Meta:
        template = 'website/blocks/embed_block.html'
        icon = 'media'
        label = _('Embed Remote Content')


class H1Block(BaseBlock):
    """
    An <h1> heading.
    """
    text = blocks.CharBlock(
        max_length=255,
        label=_('Text'),
    )

    class Meta:
        template = 'website/blocks/h1_block.html'
        icon = 'title'
        label = _('Heading 1')


class H2Block(BaseBlock):
    """
    An <h2> heading.
    """
    text = blocks.CharBlock(
        max_length=255,
        label=_('Text'),
    )

    class Meta:
        template = 'website/blocks/h2_block.html'
        icon = 'title'
        label = _('Heading 2')


class H3Block(BaseBlock):
    """
    An <h3> heading.
    """
    text = blocks.CharBlock(
        max_length=255,
        label=_('Text'),
    )

    class Meta:
        template = 'website/blocks/h3_block.html'
        icon = 'title'
        label = _('Heading 3')


class TableBlock(BaseBlock):
    table = TableBlock()

    class Meta:
        template = 'website/blocks/table_block.html'
        icon = 'list-ul'
        label = 'Table'


class ImageBlock(BaseBlock):
    """
    An <img>, by default styled responsively to fill its container.
    """
    image = ImageChooserBlock(
        label=_('Image'),
    )
    convert_to_jpeg = blocks.BooleanBlock(
        required=False,
        default=True,
        choices=page_choices['BOOLEAN_CHOICES'],
        label=_('Convert to jpeg?'),
        help_text=_('Convert to jpeg, or leave in original format?')
    )

    class Meta:
        template = 'website/blocks/image_block.html'
        icon = 'image'
        label = _('Image')


class ImageLinkBlock(BaseImagelinkBlock):
    """
    An <a> with an image inside it, instead of text.
    """
    image = ImageChooserBlock(
        label=_('Image'),
    )
    alt_text = blocks.CharBlock(
        max_length=255,
        required=True,
        help_text=_('Alternate text to show if the image doesn’t load'),
    )
    convert_to_jpeg = blocks.BooleanBlock(
        required=False,
        default=True,
        choices=page_choices['BOOLEAN_CHOICES'],
        label=_('Convert to jpeg?'),
        help_text=_('Convert to jpeg, or leave in original format?')
    )

    class Meta:
        template = 'website/blocks/image_link_block.html'
        icon = 'image'
        label = _('Image Link')
        value_class = LinkStructValue


class PageListBlock(BaseBlock):
    """
    Renders a preview of selected pages.
    """
    indexed_by = blocks.PageChooserBlock(
        required=True,
        label=_('Parent page'),
        help_text=_(
            "Show a preview of pages that are children of the selected page. Uses ordering specified in the page’s LAYOUT tab."  # noqa
        ),
    )
    show_preview = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_('Show body preview'),
    )
    num_posts = blocks.IntegerBlock(
        default=3,
        label=_('Number of pages to show'),
    )

    settings_class = OptionalColumnSettingsCards

    class Meta:
        template = 'website/blocks/pagelist_block.html'
        icon = 'list-ul'
        label = _('Latest Pages')

    def get_context(self, value, parent_context=None):

        context = super().get_context(value, parent_context=parent_context)

        indexer = value['indexed_by'].specific
        # try to use the WebPage `get_index_children()`,
        # but fall back to get_children if this is a non-WebPage
        if hasattr(indexer, 'get_index_children'):
            pages = indexer.get_index_children()
        else:
            pages = indexer.get_children().live()

        context['pages'] = pages[:value['num_posts']]
        return context


class PagePreviewBlock(BaseBlock):
    """
    Renders a preview of a specific page.
    """
    page = blocks.PageChooserBlock(
        required=True,
        label=_('Page to preview'),
        help_text=_('Show a mini preview of the selected page.'),
    )

    class Meta:
        template = 'website/blocks/pagepreview_block.html'
        icon = 'doc-empty-inverse'
        label = _('Page Preview')


class QuoteBlock(BaseBlock):
    """
    A <blockquote>.
    """
    text = blocks.TextBlock(
        required=True,
        rows=4,
        label=_('Quote Text'),
    )
    author = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_('Author'),
    )

    class Meta:
        template = 'website/blocks/quote_block.html'
        icon = 'openquote'
        label = _('Quote')


class RichTextBlock(blocks.RichTextBlock):
    
    class Meta:
        template = 'website/blocks/rich_text_block.html'

    def __init__(self, required=True, help_text=None, editor='default', features=None, validators=(), **kwargs):
        super().__init__(**kwargs)

        self.features = [
            'bold',
            'italic',
            'h1',
            'h2',
            'h3',
            'h4',
            'h5',
            'h6',
            'ol',
            'ul',
            'hr',
            'link',
            'image',
            'embed',
            'code',
            'superscript',
            'subscript',
            'strikethrough'
        ]
        


class MultiSelectBlock(blocks.FieldBlock):
    """
    Renders as MultipleChoiceField, used for adding checkboxes,
    radios, or multiselect inputs in the streamfield.
    """

    def __init__(self, required=True, help_text=None, choices=None, widget=None, **kwargs):
        self.field = forms.MultipleChoiceField(
            required=required,
            help_text=help_text,
            choices=choices,
            widget=widget,
        )
        super().__init__(**kwargs)

    def get_searchable_content(self, value):
        return [force_text(value)]


class CollectionChooserBlock(blocks.FieldBlock):
    """
    Enables choosing a wagtail Collection in the streamfield.
    """
    target_model = Collection
    widget = forms.Select

    def __init__(self, required=False, label=None, help_text=None, *args, **kwargs):
        self._required = required
        self._help_text = help_text
        self._label = label
        super().__init__(*args, **kwargs)

    @cached_property
    def field(self):
        return forms.ModelChoiceField(
            queryset=self.target_model.objects.all().order_by('name'),
            widget=self.widget,
            required=self._required,
            label=self._label,
            help_text=self._help_text,
        )

    def to_python(self, value):
        """
        Convert the serialized value back into a python object.
        """
        if isinstance(value, int):
            return self.target_model.objects.get(pk=value)
        return value

    def get_prep_value(self, value):
        """
        Serialize the model in a form suitable for wagtail's JSON-ish streamfield
        """
        if isinstance(value, self.target_model):
            return value.pk
        return value


class BaseBlock(blocks.StructBlock):

    settings_class = OptionalSettings

    settings = blocks.Block()

    def __init__(self, local_blocks=None, **kwargs):

        klassname = self.__class__.__name__.lower()
        choices = page_choices['TEMPLATES_BLOCKS'].get('*', ()) + \
            page_choices['TEMPLATES_BLOCKS'].get(klassname, ())

        if not local_blocks:
            local_blocks = ()

        local_blocks += (('settings', self.settings_class(template_choices=choices)),)

        super().__init__(local_blocks, **kwargs)

    def render(self, value, context=None):
        template = value['settings']['custom_template']

        if not template:
            template = self.get_template(context=context)
            if not template:
                return self.render_basic(value, context=context)

        if context is None:
            new_context = self.get_context(value)
        else:
            new_context = self.get_context(value, parent_context=dict(context))

        return mark_safe(render_to_string(template, new_context))


class BaseLayoutBlock(BaseBlock):
    # Subclasses can override this to provide a default list of blocks for the content.
    content_streamblocks = []

    def __init__(self, local_blocks=None, **kwargs):
        if not local_blocks and self.content_streamblocks:
            local_blocks = self.content_streamblocks

        if local_blocks:
            local_blocks = (('content', blocks.StreamBlock(local_blocks, label=_('Content'))),)

        super().__init__(local_blocks, **kwargs)



class ColumnBlock(BaseLayoutBlock):
    """
    Renders content in a column.
    """
    column_size = blocks.ChoiceBlock(
        choices=page_choices['COL_SIZE_CHOICES'],
        default=page_choices['COL_SIZE_DEFAULT'],
        required=False,
        label=_('Column size'),
    )

    settings_class = OptionalColumnSettings

    class Meta:
        template = 'website/blocks/column_block.html'
        icon = 'placeholder'
        label = 'Column'


class GridBlock(BaseLayoutBlock):
    """
    Renders a row of columns.
    """
    fluid = blocks.BooleanBlock(
        required=False,
        label=_('Full width'),
    )

    class Meta:
        template = 'website/blocks/grid_block.html'
        icon = 'placeholder'
        label = _('Responsive Grid Row')

    def __init__(self, local_blocks=None, **kwargs):
        super().__init__(
            local_blocks=[
                ('content', ColumnBlock(local_blocks))
            ]
        )


class CardGridBlock(BaseLayoutBlock):
    """
    Renders a row of cards.
    """
    column_size = blocks.ChoiceBlock(
        choices=page_choices['COL_SIZE_CHOICES'],
        default=page_choices['COL_SIZE_DEFAULT'],
        required=False,
        label=_('Column size'),
    )
    fluid = blocks.BooleanBlock(
        required=False,
        label=_('Full width'),
    )

    settings_class = OptionalColumnSettings

    class Meta:
        template = 'website/blocks/cardgrid_deck.html'
        icon = 'placeholder'
        label = _('Card Grid')


class JumbotronBlock(BaseLayoutBlock):
    """
    Wrapper with color and image background options.
    """

    fluid = blocks.BooleanBlock(
        required=False,
        default=True,
        label=_('Full width'),
    )
    is_parallax = blocks.BooleanBlock(
        required=False,
        label=_('Parallax Effect'),
        help_text=_(
            'Background images scroll slower than foreground images, creating an illusion of depth.'),  # noqa
    )
    background_image = ImageChooserBlock(required=False)
    tile_image = blocks.BooleanBlock(
        required=False,
        default=False,
        label=_('Tile background image'),
    )
    background_color = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_('Background color'),
        help_text=_('Hexadecimal, rgba, or CSS color notation (e.g. #ff0011)'),
    )
    foreground_color = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_('Text color'),
        help_text=_('Hexadecimal, rgba, or CSS color notation (e.g. #ff0011)'),
    )

    class Meta:
        template = 'website/blocks/jumbotron_block.html'
        icon = 'image'
        label = 'Jumbotron Unit'

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)

        if value['background_image']:
            context['latest_post_image'] = value['background_image']
        elif context['settings'].request_or_site.seosettings.main_entity_page.specific.get_children().live().order_by('-first_published_at')[0].specific.cover_image:
            context['latest_post_image'] = context['settings'].request_or_site.seosettings.main_entity_page.specific.get_children().live().order_by('-first_published_at')[0].specific.og_image
        elif context['settings'].request_or_site.seosettings.main_entity_page.specific.get_children().live().order_by('-first_published_at')[0].specific.og_image:
            context['latest_post_image'] = context['settings'].request_or_site.seosettings.main_entity_page.specific.get_children().live().order_by('-first_published_at')[0].specific.cover_image      
        return context


class BaseLinkBlock(BaseBlock):
    """
    Common attributes for creating a link within the CMS.
    """
    page_link = blocks.PageChooserBlock(
        required=False,
        label=_('Page link'),
    )
    doc_link = DocumentChooserBlock(
        required=False,
        label=_('Document link'),
    )
    social_link = blocks.ChoiceBlock(
        choices=page_choices['SOCIAL_LINK_CHOICES'],
        required=False,
        label=_('Social link'),
        help_text=_('Use a social media link from your site-wide settings.')
    )
    other_link = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_('Other link'),
    )

    settings_class = OptionalTrackingSettings

    class Meta:
        value_class = LinkStructValue

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)

        if value['social_link']:
            social = value['social_link']
            social_url = context['settings'].request_or_site.socialmediasettings.social_dict[social]
            context['self']['url'] = social_url
        
        return context


class LocalMediaBlock(BaseBlock):
    """
    Pass the page level media to a block template.
    """
    
    class Meta:
        template = 'website/blocks/contentpage_localmedia_block.html'
        icon = 'media'
        label = _('Embed Local Media')


class AuthorsContributorsBlock(BaseBlock):
    """
    Pass the page level media to a block template.
    """
    
    class Meta:
        template = 'website/blocks/contentpage_authors_block.html'
        icon = 'group'
        label = _('Authors & Contributors')


class ContentpageHeadingBlock(BaseBlock):
    """
    Pass the page level media to a block template.
    """
    
    class Meta:
        template = 'website/blocks/contentpage_heading_block.html'
        icon = 'title'
        label = _('Title & Heading Data')


class SearchFormBlock(BaseBlock):

    button_label = blocks.CharBlock(
        max_length=255,
        required=False,
        label=_('Button Text'),
        help_text=_('Optional custom button label, the default is "Search" if this is left blank.'),
    )

    class Meta:
        template = 'website/blocks/search_form_block.html'
        icon = 'help'
        label = _('Search Form')


class CommentBlock(BaseBlock):

    class Meta:
        template = 'website/blocks/comment_block.html'
        icon = 'tick'
        label = _('User Comments')


class BodyTextBlock(BaseLayoutBlock):

    content_streamblocks = [
        ('code', MarkdownBlock(label='Markdown', icon='pilcrow', classname='collapsible')),
        ('text', RichTextBlock(label='Rich Text', icon='doc-full', classname='collapsible'))
    ]

    class Meta:
        template = 'website/blocks/contentpage_bodytext_block.html'
        icon = 'doc-full'
        label = _('Main Body Text')



class CardBlock(BaseBlock):
    """
    A component of information with image, text, and buttons.
    """
    image = ImageChooserBlock(
        required=False,
        max_length=255,
        label=_('Image'),
    )
    title = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_('Title'),
    )
    subtitle = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_('Subtitle'),
    )
    description = blocks.RichTextBlock(
        features=['bold', 'italic', 'ol', 'ul', 'hr', 'link', 'document-link'],
        label=_('Body'),
    )
    links = blocks.StreamBlock(
        [('Links', ButtonBlock())],
        blank=True,
        required=False,
        label=_('Links'),
    )

    class Meta:
        template = 'website/blocks/card_block.html'
        icon = 'doc-empty-inverse'
        label = _('Card')


class CarouselBlock(BaseBlock):
    """
    Enables choosing a Carousel snippet.
    """
    carousel = SnippetChooserBlock('website.Carousel')

    class Meta:
        icon = 'image'
        label = _('Carousel')
        template = 'website/blocks/carousel_block.html'


class ImageGalleryBlock(BaseBlock):
    """
    Show a collection of images with interactive previews that expand to
    full size images in a modal.
    """
    collection = CollectionChooserBlock(
        required=True,
        label=_('Image Collection'),
    )

    class Meta:
        template = 'website/blocks/image_gallery_block.html'
        icon = 'image'
        label = _('Image Gallery')


class ModalBlock(ButtonMixin, BaseLayoutBlock):
    """
    Renders a button that then opens a popup/modal with content.
    """
    header = blocks.CharBlock(
        required=False,
        max_length=255,
        label=_('Modal heading'),
    )
    content = blocks.StreamBlock(
        [],
        label=_('Modal content'),
    )
    footer = blocks.StreamBlock(
        [
            ('text', blocks.CharBlock(icon='doc-full', max_length=255, label=_('Simple Text'))),  # noqa
            ('button', ButtonBlock()),
        ],
        required=False,
        label=_('Modal footer'),
    )

    class Meta:
        template = 'website/blocks/modal_block.html'
        icon = 'placeholder'
        label = _('Modal')


class NavLinkBlock(BaseLinkBlock):
    """
    External link.
    """
    link_text = blocks.CharBlock(
        required=True,
        label=_('Link Text'),
    )

    class Meta:
        template = 'website/blocks/external_link_block.html'
        label = _('External Link')


class ContentWallBlock(BaseBlock):
    """
    Enables choosing a ContentWall snippet.
    """
    content_wall = SnippetChooserBlock('website.ContentWall')
    
    class Meta:
        icon = 'no-view'
        label = _('Content Wall')
        template = 'website/blocks/content_wall_block.html'


class ReusableContentBlock(BaseBlock):
    """
    Enables choosing a ResusableContent snippet.
    """
    content = SnippetChooserBlock('website.ReusableContent')

    class Meta:
        icon = 'code'
        label = _('Reusable Content')
        template = 'website/blocks/reusable_content_block.html'


class FormBlockMixin(BaseBlock):

    class Meta:
        abstract = True

    settings_class = OptionalFormSettings


class StreamFormFieldBlock(FlexibleformBlocks.OptionalFormFieldBlock, FormBlockMixin):
    pass


class StreamFormCharFieldBlock(FlexibleformBlocks.CharFieldBlock, FormBlockMixin):

    class Meta:
        label = _("Text or Email input")
        icon = "doc-full"


class StreamFormTextFieldBlock(FlexibleformBlocks.TextFieldBlock, FormBlockMixin):

    class Meta:
        label = _("Multi-line text")
        icon = "pilcrow"


class StreamFormNumberFieldBlock(FlexibleformBlocks.NumberFieldBlock, FormBlockMixin):

    class Meta:
        label = _("Numbers only")
        icon = "order"


class StreamFormCheckboxFieldBlock(FlexibleformBlocks.CheckboxFieldBlock, FormBlockMixin):

    class Meta:
        label = _("Single Checkbox")
        icon = "tick"


class StreamFormRadioButtonsFieldBlock(FlexibleformBlocks.RadioButtonsFieldBlock, FormBlockMixin):

    class Meta:
        label = _("Radios")
        icon = "radio-empty"


class StreamFormDropdownFieldBlock(FlexibleformBlocks.DropdownFieldBlock, FormBlockMixin):

    class Meta:
        label = _("Dropdown")
        icon = "list-ul"


class StreamFormCheckboxesFieldBlock(FlexibleformBlocks.CheckboxesFieldBlock, FormBlockMixin):

    class Meta:
        label = _("Checkboxes")
        icon = "tick-inverse"


class StreamFormDateFieldBlock(FlexibleformBlocks.DateFieldBlock, FormBlockMixin):

    class Meta:
        label = _("Date")
        icon = "date"

    field_class = DateField
    widget = DateInput


class StreamFormTimeFieldBlock(FlexibleformBlocks.TimeFieldBlock, FormBlockMixin):

    class Meta:
        label = _("Time")
        icon = "time"

    field_class = TimeField
    widget = TimeInput


class StreamFormDateTimeFieldBlock(FlexibleformBlocks.DateTimeFieldBlock, FormBlockMixin):

    class Meta:
        label = _("Date and Time")
        icon = "date"

    field_class = DateTimeField
    widget = DateTimeInput


class StreamFormImageFieldBlock(FlexibleformBlocks.ImageFieldBlock, FormBlockMixin):

    class Meta:
        label = _("Image Upload")
        icon = "image"


class StreamFormStepBlock(FlexibleformBlocks.FormStepBlock):

    form_fields = blocks.StreamBlock()

    def __init__(self, local_blocks=None, **kwargs):
        super().__init__(
            local_blocks=[
                ('form_fields', blocks.StreamBlock(local_blocks))
            ]
        )


html_streamblocks = [
    ('text', RichTextBlock(icon='doc-full', classname='collapsible')),
    ('button', ButtonBlock(classname='collapsible')),
    ('image', ImageBlock(classname='collapsible')),
    ('image_link', ImageLinkBlock(classname='collapsible')),
    ('html', blocks.RawHTMLBlock(icon='code', classname='monospace, collapsible', label=_('HTML'))),
    ('download', DownloadBlock(classname='collapsible')),
    ('embed_video', EmbedBlock(classname='collapsible')),
    ('quote', QuoteBlock(classname='collapsible')),
    ('table', TableBlock(classname='collapsible')),
    ('google_map', EmbedGoogleMapBlock(classname='collapsible')),
    ('page_list', PageListBlock(classname='collapsible')),
    ('page_preview', PagePreviewBlock(classname='collapsible')),
    ('search_form', SearchFormBlock(classname='collapsible')),
]

content_streamblocks = html_streamblocks + [
    ('code', MarkdownBlock(label='Markdown', classname='collapsible')),
    ('card', CardBlock(classname='collapsible')),
    ('carousel', CarouselBlock(classname='collapsible')),
    ('image_gallery', ImageGalleryBlock(classname='collapsible')),
    ('modal', ModalBlock(html_streamblocks, classname='collapsible')),
    ('reusable_content', ReusableContentBlock(classname='collapsible')),
]

basic_layout_streamblocks = [
    ('row', GridBlock(html_streamblocks)),
    ('html', blocks.RawHTMLBlock(icon='code', classname='monospace collapsible', label=_('HTML'))),
]

header_footer_streamblocks = content_streamblocks + [
    ('link_block', NavLinkBlock(classname='collapsible'))
]

layout_streamblocks = [
    ('jumbotron', JumbotronBlock([
        ('row', GridBlock(header_footer_streamblocks)),
        ('cardgrid', CardGridBlock([
            ('card', CardBlock(classname='monospace collapsible')),
        ])),
        ('html', blocks.RawHTMLBlock(icon='code', classname='monospace collapsible', label=_('HTML'))),
    ])),
    ('row', GridBlock(header_footer_streamblocks, classname='monospace collapsible')),
    ('cardgrid', CardGridBlock([
        ('card', CardBlock(classname='collapsible')),
    ])),
    ('html', blocks.RawHTMLBlock(icon='code', classname='monospace collapsible', label=_('HTML'))),
]

streamform_fieldblocks = [
    ('sf_singleline', StreamFormCharFieldBlock(group=_('Fields'), classname='collapsible')),
    ('sf_multiline', StreamFormTextFieldBlock(group=_('Fields'), classname='collapsible')),
    ('sf_number', StreamFormNumberFieldBlock(group=_('Fields'), classname='collapsible')),
    ('sf_checkboxes', StreamFormCheckboxesFieldBlock(group=_('Fields'), classname='collapsible')),
    ('sf_radios', StreamFormRadioButtonsFieldBlock(group=_('Fields'), classname='collapsible')),
    ('sf_dropdown', StreamFormDropdownFieldBlock(group=_('Fields'), classname='collapsible')),
    ('sf_checkbox', StreamFormCheckboxFieldBlock(group=_('Fields'), classname='collapsible')),
    ('sf_date', StreamFormDateFieldBlock(group=_('Fields'), classname='collapsible')),
    ('sf_time', StreamFormTimeFieldBlock(group=_('Fields'), classname='collapsible')),
    ('sf_datetime', StreamFormDateTimeFieldBlock(group=_('Fields'), classname='collapsible')),
    ('sf_image', StreamFormImageFieldBlock(group=_('Fields'), classname='collapsible')),
    #('sf_file', StreamFormFileFieldBlock(group=_('Fields'), classname='collapsible')),
]

streamform_blocks = [
    ('step', StreamFormStepBlock(streamform_fieldblocks + html_streamblocks)),
]

contentwall_streamblocks = html_streamblocks + [
    ('code', MarkdownBlock(label='Markdown', classname='collapsible')),
    ('reusable_content', ReusableContentBlock(classname='collapsible')),
]

contentpage_streamblocks = [
    ('local_media', LocalMediaBlock(icon='media', classname='collapsible')),
    ('authors_contributors', AuthorsContributorsBlock(icon='group', classname='collapsible')),
    ('title_heading', ContentpageHeadingBlock(icon='title', classname='collapsible')),
    ('body_text', BodyTextBlock(icon='doc-full', classname='collapsible')),
    ('button', ButtonBlock(classname='collapsible')),
    ('image', ImageBlock(classname='collapsible')),
    ('image_link', ImageLinkBlock(classname='collapsible')),
    ('html', blocks.RawHTMLBlock(icon='code', classname='monospace, collapsible', label=_('HTML'))),
    ('download', DownloadBlock(classname='collapsible')),
    ('quote', QuoteBlock(classname='collapsible')),
    ('table', TableBlock(classname='collapsible')),
    ('google_map', EmbedGoogleMapBlock(classname='collapsible')),
    ('page_list', PageListBlock(classname='collapsible')),
    ('page_preview', PagePreviewBlock(classname='collapsible')),
    ('card', CardBlock(classname='collapsible')),
    ('carousel', CarouselBlock(classname='collapsible')),
    ('image_gallery', ImageGalleryBlock(classname='collapsible')),
    ('modal', ModalBlock(html_streamblocks, classname='collapsible')),
    ('reusable_content', ReusableContentBlock(classname='collapsible')),
    ('user_comments', CommentBlock(classname='collapsible')),
]
