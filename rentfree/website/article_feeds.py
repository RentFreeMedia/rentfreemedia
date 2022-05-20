import bleach
import lxml
import re
from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Rss201rev2Feed, rfc2822_date
from django.utils.text import slugify
from xml.sax.saxutils import XMLGenerator


def disallow_anchors(description):
    soup = BeautifulSoup(description, 'lxml')
    for link in soup.find_all('a'):
        if 'href' in link.attrs:
            if re.match(r'^<a\shref="\#.*?">.*?</a>$', str(link), re.IGNORECASE):
                link.replace_with_children()
            else:
                pass
        else:
            pass
    return soup.body.decode_contents()


class SimplerXMLGenerator(XMLGenerator):
    def addQuickElement(self, name, contents=None, attrs=None):
        "Convenience method for adding an element with no children"
        if attrs is None:
            attrs = {}
        self.startElement(name, attrs)
        if contents is not None:
            if contents.startswith('<![CDATA['):
                self.unescaped_characters(contents)
            else:
                self.characters(contents)
        self.endElement(name)

    def characters(self, content):
        if content and re.search(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]', content):
            # Fail loudly when content has control chars (unsupported in XML 1.0)
            # See https://www.w3.org/International/questions/qa-controls
            raise UnserializableContentError("Control characters are not supported in XML 1.0")
        XMLGenerator.characters(self, content)

    def unescaped_characters(self, content):
        if content and re.search(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]', content):
            # Fail loudly when content has control chars (unsupported in XML 1.0)
            # See https://www.w3.org/International/questions/qa-controls
            raise UnserializableContentError("Control characters are not supported in XML 1.0")
        XMLGenerator.ignorableWhitespace(self, content)

    def startElement(self, name, attrs):
        # Sort attrs for a deterministic output.
        sorted_attrs = dict(sorted(attrs.items())) if attrs else attrs
        super().startElement(name, sorted_attrs)

class ArticleFeedGenerator(Rss201rev2Feed):

    def rss_attributes(self):
        return {
            'version': self._version,
            'xmlns:dc': 'http://purl.org/dc/elements/1.1/',
        }

    def add_root_elements(self, handler):
        handler.addQuickElement("title", self.feed['title'])
        handler.addQuickElement("link", self.feed['link'])
        handler.addQuickElement("description", self.feed['description'])
        if self.feed['author_email'] is not None:
            handler.addQuickElement("author", self.feed['author_email'])
        if self.feed['feed_copyright'] is not None:
            handler.addQuickElement("copyright", self.feed['feed_copyright'])
        if settings.LANGUAGE_CODE is not None:
            handler.addQuickElement("language", settings.LANGUAGE_CODE)
        if self.feed['rss_categories'] is not None:
            tags = []
            for tag in self.feed['rss_categories']:
                tags += tag.name
            tags = ''.join(tags).replace(' ', '/')
            handler.addQuickElement("category", tags)
        if self.feed['rss_editor_email'] is not None:
            handler.addQuickElement("managingEditor", self.feed['rss_editor_email'])
        if self.latest_post_date:
            handler.addQuickElement("lastBuildDate", rfc2822_date(self.latest_post_date()))
        if self.feed['ttl'] is not None:
            handler.addQuickElement("ttl", self.feed['ttl'])
        if self.feed['rss_image_url'] is not None:    
            handler.startElement("image", {})
            handler.addQuickElement("url", self.feed['rss_image_url'])
            handler.addQuickElement("title", self.feed['title'])
            handler.addQuickElement("link", self.feed['link'])
            handler.endElement("image")

    def add_item_elements(self, handler, item):

        handler.addQuickElement("title", item['title'])
        handler.addQuickElement("link", item['link'])
        if item['description'] is not None:
            description = (bleach.clean(item['description'].replace('</p>', '</p><br />'), strip=True, tags=['p', 'ul', 'li', 'a', 'br'])).lstrip()
            description_stripped = disallow_anchors(description)
            handler.addQuickElement("description", '<![CDATA[' + description_stripped + ']]>')
        # Author information.
        if item['item_authors'] is not None:
            for author in item['item_authors']:
                if author.first_name and author.last_name:
                    handler.addQuickElement("dc:creator", author.first_name + ' ' + author.last_name)
                else:
                    handler.addQuickElement("dc:creator", author.user_name)
        if item['item_contributors'] is not None:
            for contributor in item['item_contributors']:
                if contributor.contributor_display:
                    handler.addQuickElement("dc:contributor", contributor.contributor_display)
                elif contributor.first_name and contributor.last_name:
                    handler.addQuickElement("dc:contributor", contributor.first_name + ' ' + contributor.last_name)
                else:
                    handler.addQuickElement("dc:contributor", contributor.user_name)
        if item['pubdate'] is not None:
            handler.addQuickElement("pubDate", rfc2822_date(item['pubdate']))
        if item['comments'] is not None:
            handler.addQuickElement("comments", item['comments'])
        if item['unique_id'] is not None:
            guid_attrs = {}
            if isinstance(item.get('unique_id_is_permalink'), bool):
                guid_attrs['isPermaLink'] = str(item['unique_id_is_permalink']).lower()
            handler.addQuickElement("guid", item['unique_id'], guid_attrs)
        if item['ttl'] is not None:
            handler.addQuickElement("ttl", item['ttl'])

        # Enclosure.
        if len(item['enclosures']) > 0:
            enclosures = list(item['enclosures'])
            if len(enclosures) > 1:
                raise ValueError(
                    "RSS feed items may only have one enclosure, see "
                    "http://www.rssboard.org/rss-profile#element-channel-item-enclosure"
                )
            enclosure = enclosures[0]
            handler.addQuickElement('enclosure', '', {
                'url': enclosure.url,
                'length': enclosure.length,
                'type': enclosure.mime_type,
            })

        # Categories.
        if item['categories'] is not None:
            for cat in item['categories']:
                handler.addQuickElement("category", cat)

    def write(self, outfile, encoding):
        handler = SimplerXMLGenerator(outfile, encoding)
        handler.startDocument()
        handler.startElement("rss", self.rss_attributes())
        handler.startElement("channel", self.root_attributes())
        self.add_root_elements(handler)
        self.write_items(handler)
        self.endChannelElement(handler)
        handler.endElement("rss")


class ArticleFeed(Feed):
    """
    Serves an RSS feed for a public podcast index page in Wagtail with a routable url that calls this feed.
    Note required data being passed to __init__: first = first post in the feed, use .specific() to get the 
    proper model, not the root 'Page' model!  last = last post in the feed. link = the full url to the index
    page, which you can get within the routable page def via request.get_raw_uri(). 
    """
    feed_type = ArticleFeedGenerator
    language = settings.LANGUAGE_CODE

    def __init__(self, request, rss_link, home_link, all_public, all_private, tags, uidb64, token):
        
        if uidb64 and token:
            queryset_base = all_private
        else:
            queryset_base = all_public

        self.request = request
        self.all_public = all_public
        self.all_private = all_private
        self.first = queryset_base.first()
        self.last = queryset_base.last()
        self.home_link = home_link
        self.rss_link = rss_link
        self.tags = tags
        self.index_page = self.first.get_parent().specific if self.first else None
        self.token = token
        self.uidb64 = uidb64

    def author_email(self):
        if self.index_page.rss_author:
            return self.index_page.rss_author
        else:
            return None

    def author_name(self):
        if self.index_page.rss_author.first_name and self.index_page.rss_author.last_name:
            return self.index_page.rss_author.first_name + ' ' + self.index_page.rss_author.last_name
        elif self.index.rss_author.user_name:
            return self.index_page.rss_author.user_name
        else:
            return None

    def description(self):
        if self.index_page.rss_description:
            return self.index_page.rss_description
        else:
            return None

    def feed_copyright(self):
        if self.index_page.rss_copyright:
            copyright_string = self.index_page.rss_copyright
        else:
            copyright_string = self.index_page.rss_title
        last_year = str(self.last.first_published_at.year)
        first_year = str(self.first.first_published_at.year)
        if last_year == first_year:
            return first_year + ', ' + copyright_string
        else:
            return first_year + '-' + last_year + ', ' + copyright_string

    def get_object(self, request):
        return self.all_public

    def link(self):
        return self.home_link

    def feed_url(self):
        return self.rss_link

    def title(self):
        return self.index_page.rss_title

    def ttl(self):
        return self.index_page.rss_ttl

    def item_link(self, item):
        if item.personalisation_metadata.is_canonical:
            return item.full_url
        else:
            return item.personalisation_metadata.canonical_page.full_url

    def items(self):
        if self.all_public and self.all_private:
            return self.all_public | self.all_private
        elif self.all_public and not self.all_private:
            return self.all_public
        elif self.all_private and not self.all_public:
            return self.all_private

    def item_title(self, item):
        if item.personalisation_metadata.is_canonical:
            return item.title
        else:
            return item.personalisation_metadata.canonical_page.title

    def item_description(self, item):
        item_bodytext = item.body.render_as_block()
        soup = BeautifulSoup(item_bodytext, 'lxml')
        soup_body = str(soup.select_one('.block-body_text'))
        item.bodytext = bleach.clean(soup_body, strip=True, tags=['p', 'ul', 'li', 'a', 'br']).lstrip()

        return '<p>' + item.caption + '</p>' + item.bodytext

    def item_enclosure_url(self, item):
        if item.personalisation_metadata.is_canonical:
            if item.remote_media:
                if item.remote_media_type != 'youtube' and item.remote_media_type != 'vimeo':
                    return item.remote_media
                else:
                    return None
            elif item.uploaded_media:
                return item.uploaded_media.url
            else:
                return None
        else:
            if item.remote_media:
                if item.remote_media_type != 'youtube' and item.remote_media_type != 'vimeo':
                    return item.remote_media
                else:
                    return None
            elif item.uploaded_media:
                return 'https://' + self.request.get_host() + '/premium_media/' + self.uidb64 + '/' + str(item.uploaded_media.id) + '/' + self.token + '/' + item.uploaded_media.filename
            else:
                return None
 
    def item_enclosure_length(self, item):
        if item.remote_media:
            if item.remote_media_type != 'youtube' and item.remote_media_type != 'vimeo':
                return item.remote_media_size
            else:
                return None
        elif item.uploaded_media:
            return item.uploaded_media.file.size
        else:
            return None

    def item_enclosure_mime_type(self, item):
        if item.remote_media:
            if item.remote_media_type != 'youtube' and item.remote_media_type != 'vimeo':
                return item.remote_media_type
            else:
                return None
        elif item.uploaded_media:
            return item.uploaded_media_type
        else:
            return None

    def item_guid(self, item):
        return slugify(self.index_page.rss_title) + '-' + str(item.guid)

    def item_guid_is_permalink(self, item):
        return False

    def item_pubdate(self, item):
        return item.first_published_at

    def item_categories(self, item):
        if item.tags and self.index_page.rss_categories:
            return item.tags.names()
        else:
            return None

    def item_comments(self, item):
        if item.personalisation_metadata.is_canonical:
            return item.full_url + '#comments'
        else:
            return item.personalisation_metadata.canonical_page.full_url + '#comments'


    def feed_extra_kwargs(self, obj):
        return {
            'rss_image_url': self.index_page.rss_image.get_rendition('fill-1440x1440|format-jpeg|jpegquality-80').url if self.index_page.rss_image else None,
            'rss_categories': self.tags if (self.tags and self.index_page.rss_categories) else None,
            'rss_editor_email': self.index_page.rss_editor.email if self.index_page.rss_editor else None,
        }

    def item_extra_kwargs(self, item):
        return {
            'item_authors': item.author.all() if item.author.first() else None,
            'item_contributors': item.contributor.all() if item.contributor.first() else None
        }
