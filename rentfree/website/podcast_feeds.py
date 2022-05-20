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

class iTunesPodcastsFeedGenerator(Rss201rev2Feed):

    def rss_attributes(self):
        return {
            'version': self._version,
            'xmlns:itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd',
            'xmlns:dc': 'http://purl.org/dc/elements/1.1/',
            'xmlns:googleplay': 'http://www.google.com/schemas/play-podcasts/1.0',
            'xmlns:spotify': 'http://www.spotify.com/ns/rss',
            'xmlns:media': 'http://search.yahoo.com/mrss/',
        }

    def add_root_elements(self, handler):
        handler.addQuickElement("title", self.feed['title'])
        handler.addQuickElement("link", self.feed['link'])
        handler.addQuickElement("description", '<![CDATA[' + (bleach.clean(self.feed['description'], strip=True, tags=['p', 'ul', 'li', 'a', 'br'])).lstrip() + ']]>')
        if self.feed['language'] is not None:
            handler.addQuickElement("language", self.feed['language'])
        for cat in self.feed['categories']:
            handler.addQuickElement("category", cat)
        if self.feed['itunes_type'] is not None:
            handler.addQuickElement("itunes:type", self.feed['itunes_type'])
        if self.feed['itunes_author'] is not None:
            handler.addQuickElement('itunes:author', self.feed['itunes_author'])
        if self.feed['itunes_email'] is not None or self.feed['itunes_name'] is not None:
            handler.startElement("itunes:owner", {})
            if self.feed['itunes_email'] is not None:
                handler.addQuickElement("itunes:email", self.feed['itunes_email'])
            handler.endElement("itunes:owner")
        if self.feed['itunes_primary_category'] is not None and self.feed['itunes_primary_subcategory'] is not None:
            if self.feed['itunes_primary_category'] != 'Goverment' and self.feed['itunes_primary_category'] != 'History' and self.feed['itunes_primary_category'] != 'Technology' and self.feed['itunes_primary_category'] != 'True Crime':  
                handler.startElement("itunes:category", {"text": self.feed['itunes_primary_category']})
                handler.addQuickElement("itunes:category", None, {"text": self.feed['itunes_primary_subcategory']})
                handler.endElement("itunes:category")
            else:
                handler.addQuickElement("itunes:category", None, {"text": self.feed['itunes_primary_category']})
        elif self.feed['itunes_primary_category'] is not None and self.feed['itunes_primary_subcategory'] is None:
            handler.addQuickElement("itunes:category", None, {"text": self.feed['itunes_primary_category']})
        if self.feed['itunes_secondary_category'] is not None and self.feed['itunes_secondary_subcategory'] is not None:
            if self.feed['itunes_secondary_category'] != 'Goverment' and self.feed['itunes_secondary_category'] != 'History' and self.feed['itunes_secondary_category'] != 'Technology' and self.feed['itunes_secondary_category'] != 'True Crime':  
                handler.startElement("itunes:category", {"text": self.feed['itunes_secondary_category']})
                handler.addQuickElement("itunes:category", None, {"text": self.feed['itunes_secondary_subcategory']})
                handler.endElement("itunes:category")
            else:
                handler.addQuickElement("itunes:category", None, {"text": self.feed['itunes_secondary_category']})
        elif self.feed['itunes_secondary_category'] is not None and self.feed['itunes_secondary_subcategory'] is None:
            handler.addQuickElement("itunes:category", None, {"text": self.feed['itunes_secondary_category']})
        if self.feed['googleplay_category'] is not None:
            handler.addQuickElement("googleplay:category", None, {"text": self.feed['googleplay_category']})
        if self.feed['itunes_explicit'] is not None:
            handler.addQuickElement("itunes:explicit", self.feed['itunes_explicit'])
        if self.feed['googleplay_explicit'] is not None:
            handler.addQuickElement("googleplay:explicit", self.feed['googleplay_explicit'])
        if self.feed['feed_copyright'] is not None:
            handler.addQuickElement("copyright", self.feed['feed_copyright'])
        if self.latest_post_date:
            handler.addQuickElement("lastBuildDate", rfc2822_date(self.latest_post_date()))
        if self.feed['ttl'] is not None:
            handler.addQuickElement("ttl", self.feed['ttl'])
        if self.feed['itunes_image_url'] is not None:
            handler.addQuickElement("itunes:image", None, {"href": self.feed['itunes_image_url']})
        if self.feed['rss_image_url'] is not None:    
            handler.startElement("image", {})
            handler.addQuickElement("url", self.feed['rss_image_url'])
            handler.addQuickElement("title", self.feed['title'])
            handler.addQuickElement("link", self.feed['link'])
            handler.endElement("image")

    def add_item_elements(self, handler, item):

        if self.feed['rss_preview_text'] is not None and item['item_preview']:
            handler.addQuickElement("title", self.feed['rss_preview_text'] + ' ' + item['title'])
        else:
            handler.addQuickElement("title", item['title'])
        handler.addQuickElement("link", item['link'])
        if item['item_season'] is not None:
            handler.addQuickElement("itunes:season", item['item_season'])
        if item['item_epnum'] is not None:
            handler.addQuickElement("itunes:episode", item['item_epnum'])
        if item['description'] is not None:
            description = (bleach.clean(item['description'].replace('</p>', '</p><br />'), strip=True, tags=['p', 'ul', 'li', 'a', 'br'])).lstrip()
            description_stripped = disallow_anchors(description)
            handler.addQuickElement("description", '<![CDATA[' + description_stripped + ']]>')
        # Author information.
        if item['item_episode_type'] is not None:
           handler.addQuickElement("itunes:episodeType", item['item_episode_type'])
        for author in item["item_authors"]:
            if author.author_display:
                handler.addQuickElement("dc:creator", author.author_display)
            elif author.first_name and author.last_name:
                handler.addQuickElement("dc:creator", author.first_name + ' ' + author.last_name)
            elif author.user_name:
                handler.addQuickElement("dc:creator", author.user_name)
            else:
                author.first_name
        if item["item_contributors"]:
            for contributor in item["item_contributors"]:
                if contributor.contributor_display:
                    handler.addQuickElement("dc:contributor", contributor.contributor_display)
                elif contributor.first_name and contributor.last_name:
                    handler.addQuickElement("dc:contributor", contributor.first_name + ' ' + contributor.last_name)
                else:
                    handler.addQuickElement("dc:contributor", contributor.user_name)
        if item['item_duration'] is not None:
            handler.addQuickElement("itunes:duration", item['item_duration'])
        if item['item_uploaded_image'] is not None:
            handler.addQuickElement("itunes:image", None, {"href": item['item_uploaded_image']})
        if item['item_remote_image'] is not None:
            handler.addQuickElement("itunes:image", None, {"href": item['item_remote_image']})
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
        if item['enclosures']:
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


class PodcastFeed(Feed):
    """
    Serves an RSS feed for a public podcast index page in Wagtail with a routable url that calls this feed.
    Note required data being passed to __init__: first = first post in the feed, use .specific() to get the 
    proper model, not the root 'Page' model!  last = last post in the feed. link = the full url to the index
    page, which you can get within the routable page def via request.get_raw_uri(). 
    """
    feed_type = iTunesPodcastsFeedGenerator
    language = settings.LANGUAGE_CODE

    def __init__(self, request, rss_link, home_link, all_public, all_private, token, uidb64):

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
        self.index_page = self.first.get_parent().specific if self.first else None
        self.token = token
        self.uidb64 = uidb64

    def author_name(self):
        if self.index_page.rss_itunes_author:
            return self.index_page.rss_itunes_author
        else:
            return self.index_page.rss_title

    def description(self):
        if self.index_page.rss_itunes_description:
            return self.index_page.rss_itunes_description
        else:
            return self.index_page.rss_description

    def feed_copyright(self):
        if self.index_page.rss_itunes_copyright:
            copyright_string = self.index_page.rss_itunes_copyright
        else:
            copyright_string = self.index_page.rss_title
        last_year = str(self.last.first_published_at.year)
        first_year = str(self.first.first_published_at.year)
        if last_year == first_year:
            return first_year + ', ' + copyright_string
        else:
            return first_year + '-' + last_year + ', ' + copyright_string

    def get_object(self, request):
        if self.all_public and self.all_private:
            return self.all_public | self.all_private
        elif self.all_public and not self.all_private:
            return self.all_public
        elif self.all_private and not self.all_public:
            return self.all_private
        else:
            return None

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

    def item_comments(self, item):
        if item.personalisation_metadata.is_canonical:
            return item.full_url + '#comments'
        else:
            return item.personalisation_metadata.canonical_page.full_url + '#comments'


    def feed_extra_kwargs(self, obj):
        return {
            'itunes_type': self.index_page.rss_itunes_type if self.index_page.rss_itunes_type else None,
            'itunes_author': self.index_page.rss_itunes_author if self.index_page.rss_itunes_author else self.index_page.rss_title,
            'itunes_name': self.index_page.rss_itunes_owner if self.index_page.rss_itunes_owner else self.index_page.rss_title,
            'itunes_email': self.index_page.rss_itunes_owner_email.email if self.index_page.rss_itunes_owner_email else settings.EMAIL_ADDR,
            'itunes_image_url': self.index_page.rss_premium_image.get_rendition('fill-3000x3000|jpegquality-60').url if self.token and self.uidb64 and self.index_page.rss_premium_image else self.index_page.rss_image.get_rendition('fill-3000x3000|format-jpeg|jpegquality-80').url,
            'rss_image_url': self.index_page.rss_premium_image.get_rendition('fill-1440x1440|jpegquality-60').url if self.token and self.uidb64 and self.index_page.rss_premium_image else self.index_page.rss_image.get_rendition('fill-1440x1440|format-jpeg|jpegquality-80').url,
            'itunes_explicit': str(self.index_page.rss_itunes_explicit).lower(),
            'googleplay_explicit': 'yes' if self.index_page.rss_itunes_explicit else 'no',
            'itunes_primary_category': self.index_page.rss_itunes_primary_category if self.index_page.rss_itunes_primary_category else None,
            'itunes_primary_subcategory': self.index_page.rss_itunes_primary_subcategory if self.index_page.rss_itunes_primary_subcategory else None,
            'itunes_secondary_category': self.index_page.rss_itunes_secondary_category if self.index_page.rss_itunes_secondary_category else None,
            'itunes_secondary_subcategory': self.index_page.rss_itunes_secondary_subcategory if self.index_page.rss_itunes_secondary_subcategory else None,
            'googleplay_category': self.index_page.rss_google_category if self.index_page.rss_google_category else None,
            'rss_preview_text': self.index_page.rss_preview_text if self.index_page.rss_preview_text else None
        }

    def item_extra_kwargs(self, item):
        return {
            'item_season': str(item.season_number) if item.season_number else None,
            'item_epnum': str(item.episode_number) if (item.episode_number and self.index_page.rss_include_episode_number) else None,
            'item_preview': item.episode_preview if item.episode_preview else None,
            'item_remote_image': item.remote_media_thumbnail.get_rendition('fill-3000x3000|jpegquality-60').url if (item.remote_media and item.remote_media_thumbnail) else None,
            'item_uploaded_image': item.uploaded_media.thumbnail.get_rendition('fill-3000x3000|jpegquality-60').url if (item.uploaded_media and item.uploaded_media.thumbnail) else None,
            'item_duration': str(item.remote_media_duration) if item.remote_media_duration else item.uploaded_media.duration if item.uploaded_media.duration else None,
            'item_authors': item.author.all() if item.author.first() else None,
            'item_contributors': item.contributor.all() if item.contributor.first() else None,
            'item_episode_type': item.episode_type if item.episode_type else None
        }
