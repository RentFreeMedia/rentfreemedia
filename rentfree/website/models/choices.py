from django.conf import settings
from functools import lru_cache
from pathlib import Path


BASE_DIR = settings.BASE_DIR if getattr(settings, 'BASE_DIR') else Path(__file__).resolve().parent.parent


DEFAULTS = {
    'BOOLEAN_CHOICES': (
        (True, 'Yes'),
        (False, 'No'),
    ),
    
    'RSS_ITUNES_TYPE_CHOICES': (
        ('episodic', 'Episode'),
        ('serial', 'Serial'),
    ),

    'RSS_ITUNES_CATEGORY_CHOICES': (
        ('Arts', 'Arts'),
        ('Business', 'Business'),
        ('Comedy', 'Comedy'),
        ('Education', 'Education'),
        ('Fiction', 'Fiction'),
        ('Government', 'Government'),
        ('History', 'History'),
        ('Health & Fitness', 'Health & Fitness'),
        ('Kids &amp; Family', 'Kids & Family'),
        ('Leisure', 'Leisure'),
        ('Music', 'Music'),
        ('News', 'News'),
        ('Religion & Spirituality', 'Religion & Spirituality'),
        ('Science', 'Science'),
        ('Society & Culture', 'Society & Culture'),
        ('Sports', 'Sports'),
        ('Technology', 'Technology'),
        ('True Crime', 'True Crime'),
        ('TV & Film', 'TV & Film'),
    ),

    'RSS_GOOGLE_CATEGORY_CHOICES': (
        ('Arts', 'Arts'),
        ('Business', 'Business'),
        ('Comedy', 'Comedy'),
        ('Education', 'Education'),
        ('Games & Hobbies', 'Games & Hobbies'),
        ('Government Organizations', 'Government Organizations'),
        ('Health', 'Health'),
        ('Kids & Family', 'Kids & Family'),
        ('Music', 'Music'),
        ('News & Politics', 'News & Politics'),
        ('Religion & Spirituality', 'Religion & Spirituality'),
        ('Science & Medicine', 'Science & Medicine'),
        ('Society & Culture', 'Society & Culture'),
        ('Sports & Recreation', 'Sports & Recreation'),
        ('TV & Film', 'TV & Film'),
        ('Technology', 'Technology'),
    ),

    'RSS_ITUNES_SUBCATEGORY_CHOICES': (
        ('Books', 'Arts > Books'),
        ('Design', 'Arts > Design'),
        ('Fashion &amp; Beauty', 'Arts > Fashion & Beauty'),
        ('Food', 'Arts > Food'),
        ('Performing Arts', 'Arts > Performing Arts'),
        ('Visual Arts', 'Arts > Visual Arts'),
        ('Careers', 'Business > Careers'),
        ('Entrepreneurship', 'Business > Entrepreneurship'),
        ('Business', 'Business > Investing'),
        ('Management', 'Business > Management'),
        ('Marketing', 'Business > Marketing'),
        ('Non-Profit', 'Business > Non-Profit'),
        ('Comedy Interviews', 'Comedy > Comedy Interviews'),
        ('Improv', 'Comedy > Improv'),
        ('Stand-Up', 'Comedy > Stand-Up'),
        ('Courses', 'Education > Courses'),
        ('How To', 'Education > How To'),
        ('Language Learning', 'Education > Language Learning'),
        ('Self-Improvement', 'Education > Self-Improvement'),
        ('Comedy Fiction', 'Fiction > Comedy Fiction'),
        ('Drama', 'Fiction > Drama'),
        ('Science Fiction', 'Fiction > Science Fiction'),
        ('Alternative Health', 'Health & Fitness > Alternative Health'),
        ('Fitness', 'Health & Fitness > Fitness'),
        ('Medicine', 'Health & Fitness > Medicine'),
        ('Mental Health', 'Health & Fitness > Mental Health'),
        ('Nutrition', 'Health & Fitness > Nutrition'),
        ('Sexuality', 'Health & Fitness > Sexuality'),
        ('Education for Kids', 'Kids & Family > Education for Kids'),
        ('Parenting', 'Kids & Family > Parenting'),
        ('Pets & Animals', 'Kids & Family > Pets & Animals'),
        ('Stories for Kids', 'Kids & Family > Stories for Kids'),
        ('Animation & Manga', 'Leisure > Animation & Manga'),
        ('Automotive', 'Leisure > Automotive'),
        ('Aviation', 'Leisure > Aviation'),
        ('Crafts', 'Leisure > Crafts'),
        ('Games', 'Leisure > Games'),
        ('Hobbies', 'Leisure > Hobbies'),
        ('Home & Garden', 'Leisure > Home & Garden'),
        ('Video Games', 'Leisure > Video Games'),
        ('Music Commentary', 'Leisure > Music Commentary'),
        ('Music History', 'Leisure > Music History'),
        ('Music Interviews', 'Leisure > Music Interviews'),
        ('Business News', 'News > Business News'),
        ('Daily News', 'News > Daily News'),
        ('Entertainment News', 'News > Entertainment News'),
        ('News Commentary', 'News > News Commentary'),
        ('Politics', 'News > Politics'),
        ('Sports News', 'News > Sports News'),
        ('Tech News', 'News > Tech News'),
        ('Buddhism', 'Religion & Spirituality > Buddhism'),
        ('Christianity', 'Religion & Spirituality > Christianity'),
        ('Hinduism', 'Religion & Spirituality > Hinduism'),
        ('Islam', 'Religion & Spirituality > Islam'),
        ('Judaism', 'Religion & Spirituality > Judaism'),
        ('Religion', 'Religion & Spirituality > Religion'),
        ('Spirituality', 'Religion & Spirituality > Spirituality'),
        ('Astronomy', 'Science > Astronomy'),
        ('Chemistry', 'Science > Chemistry'),
        ('Earth Sciences', 'Science > Earth Sciences'),
        ('Life Sciences', 'Science > Life Sciences'),
        ('Mathematics', 'Science > Mathematics'),
        ('Natural Sciences', 'Science > Natural Sciences'),
        ('Nature', 'Science > Nature'),
        ('Physics', 'Science > Physics'),
        ('Social Sciences', 'Science > Social Sciences'),
        ('Documentary', 'Society & Culture > Documentary'),
        ('Personal Journals', 'Society & Culture > Personal Journals'),
        ('Philosophy', 'Society & Culture > Philosophy'),
        ('Places & Travel', 'Society & Culture > Places & Travel'),
        ('Relationships', 'Society & Culture > Relationships'),
        ('Baseball', 'Sports > Baseball'),
        ('Basketball', 'Sports > Basketball'),
        ('Cricket', 'Sports > Cricket'),
        ('Fantasy Sports', 'Sports > Fantasy Sports'),
        ('Football', 'Sports > Football'),
        ('Golf', 'Sports > Golf'),
        ('Hockey', 'Sports > Hockey'),
        ('Rugby', 'Sports > Rugby'),
        ('Running', 'Sports > Running'),
        ('Soccer', 'Sports > Socer'),
        ('Swimming', 'Sports > Swimming'),
        ('Tennis', 'Sports > Tennis'),
        ('Volleyball', 'Sports > Volleyball'),
        ('Wilderness', 'Sports > Wilderness'),
        ('Wrestling', 'Sports > Wrestling'),
        ('After Shows', 'TV & Film > After Shows'),
        ('Film History', 'TV & Film > Film History'),
        ('Film Interviews', 'TV & Film > Film Interviews'),
        ('Film Reviews', 'TV & Film > Film Reviews'),
        ('TV Reviews', 'TV & Film > TV Reviews'),
    ),

    'MEDIA_CONTENT_TYPE_CHOICES': (
        ('audio/x-m4a', 'audio/mp4'),
        ('audio/mpeg', 'audio/mp3'),
        ('audio/ogg', 'audio/ogg'),
        ('audio/wav', 'audio/wav'),
        ('youtube', 'youtube'),
        ('vimeo', 'vimeo'),
        ('video/x-m4v', 'video/mp4'),
        ('video/ogg', 'video/ogg'),
        ('video/webm', 'video/webm'),
        ('video/3gpp', 'video/3gp'),
    ),

    'PROTECTED_MEDIA_URL': '/protected/',
    'PROTECTED_MEDIA_ROOT': [BASE_DIR / 'protected'],
    'PROTECTED_MEDIA_UPLOAD_WHITELIST': [],
    'PROTECTED_MEDIA_UPLOAD_BLACKLIST': ['.sh', '.exe', '.bat', '.ps1', '.app', '.jar', '.py', '.php', '.pl', '.rb'],
    
    'BUTTON_SIZE_DEFAULT': '',
    'BUTTON_SIZE_CHOICES': (
        ('btn-sm', 'Small'),
        ('', 'Default'),
        ('btn-lg', 'Large'),
    ),

    'BUTTON_STYLE_DEFAULT': 'btn-primary',
    'BUTTON_STYLE_CHOICES': (
        ('btn-primary', 'Primary'),
        ('btn-secondary', 'Secondary'),
        ('btn-success', 'Success'),
        ('btn-danger', 'Danger'),
        ('btn-warning', 'Warning'),
        ('btn-info', 'Info'),
        ('btn-link', 'Link'),
        ('btn-light', 'Light'),
        ('btn-dark', 'Dark'),
        ('btn-outline-primary', 'Outline Primary'),
        ('btn-outline-secondary', 'Outline Secondary'),
        ('btn-outline-success', 'Outline Success'),
        ('btn-outline-danger', 'Outline Danger'),
        ('btn-outline-warning', 'Outline Warning'),
        ('btn-outline-info', 'Outline Info'),
        ('btn-outline-light', 'Outline Light'),
        ('btn-outline-dark', 'Outline Dark'),
    ),

    'BUTTON_ICON_COLOR_CHOICES': (
        ('"currentColor"', 'Button Class Color'),
        ('var(--bs-primary)', 'Primary'),
        ('var(--bs-secondary)', 'Secondary'),
        ('var(--bs-success)', 'Success'),
        ('var(--bs-info)', 'Info'),
        ('var(--bs-warning)', 'Warning'),
        ('var(--bs-danger)', 'Danger'),
        ('var(--bs-light)', 'Light'),
        ('var(--bs-dark)', 'Dark'),
    ),

    'SOCIAL_LINK_CHOICES': (
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('instagram', 'Instagram'),
        ('tiktok', 'TikTok'),
        ('reddit', 'Reddit'),
        ('snapchat', 'Snapchat'),
        ('wikipedia', 'Wikipedia'),
        ('youtube', 'Youtube'),
        ('linkedin', 'LinkedIn'),
        ('google', 'Google Business'),
    ),

    'CAROUSEL_FX_DEFAULT': '',
    'CAROUSEL_FX_CHOICES': (
        ('', 'Slide'),
        ('carousel-fade', 'Fade'),
    ),

    'COL_SIZE_DEFAULT': '',
    'COL_SIZE_CHOICES': (
        ('', 'Automatically size'),
        ('12', 'Full row'),
        ('6', 'Half - 1/2 column'),
        ('4', 'Thirds - 1/3 column'),
        ('8', 'Thirds - 2/3 column'),
        ('3', 'Quarters - 1/4 column'),
        ('9', 'Quarters - 3/4 column'),
        ('2', 'Sixths - 1/6 column'),
        ('10', 'Sixths - 5/6 column'),
        ('1', 'Twelfths - 1/12 column'),
        ('5', 'Twelfths - 5/12 column'),
        ('7', 'Twelfths - 7/12 column'),
        ('11', 'Twelfths - 11/12 column'),
    ),

    'COL_BREAK_DEFAULT': 'md',
    'COL_BREAK_CHOICES': (
        ('', 'Always expanded'),
        ('sm', 'sm - Expand on small screens (phone, 576px) and larger'),
        ('md', 'md - Expand on medium screens (tablet, 768px) and larger'),
        ('lg', 'lg - Expand on large screens (laptop, 992px) and larger'),
        ('xl', 'xl - Expand on extra large screens (wide monitor, 1200px)'),
    ),

    'EMBED_WIDTH_DEFAULT': '',
    'EMBED_WIDTH_CHOICES': (
        ('', 'Default'),
        ('256', '256px'),
        ('512', '512px'),
        ('768', '768px'),
        ('1024', '1024px'),
        ('1280', '1280px'),
        ('1920', '1920px'),
        ('3840', '3840px'),
    ),

    'PROTECTED_MEDIA_URL': '/protected/',
    'PROTECTED_MEDIA_ROOT': [BASE_DIR / 'protected'],
    'PROTECTED_MEDIA_UPLOAD_WHITELIST': [],
    'PROTECTED_MEDIA_UPLOAD_BLACKLIST': ['.sh', '.exe', '.bat', '.ps1', '.app', '.jar', '.py', '.php', '.pl', '.rb'],


    'TEMPLATES_BLOCKS': {
        'bodytextblock': (
            ('website/blocks/contentpage_bodytext_block.html', 'Plain text'),
        ),
        'cardblock': (
            ('website/blocks/card_block.html', 'Card with top photo'),
            ('website/blocks/card_head.html', 'Card with header'),
            ('website/blocks/card_foot.html', 'Card with footer'),
            ('website/blocks/card_head_foot.html', 'Card with header and footer'),
            ('website/blocks/card_blurb.html', 'Blurb - rounded image and no border'),
            ('website/blocks/card_img.html', 'Cover image - use image as background'),
        ),
        'cardgridblock': (
            ('website/blocks/cardgrid_group.html', 'Card group - attached cards of equal size'),
            ('website/blocks/cardgrid_deck.html', 'Card deck - separate cards of equal size'),
        ),
        'pagelistblock': (
            ('website/blocks/pagelist_block.html', 'General, simple list'),
            ('website/blocks/pagelist_block_group.html', 'General, list group navigation panel'),
            ('website/blocks/pagelist_block_media.html', 'Content, media format'),
            ('website/blocks/pagelist_block_card_group.html',
                'Content, card group - attached cards of equal size'),
            ('website/blocks/pagelist_block_card_deck.html',
             'Content, card deck - separate cards of equal size'),
        ),
        'pagepreviewblock': (
            ('website/blocks/pagepreview_block_card.html', 'Card'),
            ('website/blocks/pagepreview_block_form.html', 'Form inputs'),
        ),
        # templates that are available for all block types
        '*': (
            ('', 'Default'),
        ),
    },

    'TEMPLATES_PAGES': {
        # templates that are available for all page types
        '*': (
            ('', 'Default'),
            ('website/pages/web_page.html', 'Web page with title data'),
            ('website/pages/web_page_notitle.html', 'Web page without title data'),
            ('website/pages/home_page.html', 'Home page - no title data, includes head RSS feeds'),
            ('website/pages/base.html', 'Base page - no container, no title, no header, no footer'),
        ),
    },

    'BANNER': None,
    'BANNER_BACKGROUND': '#f00',
    'BANNER_TEXT_COLOR': '#fff',
}


@lru_cache()
def get_config():
    config = DEFAULTS.copy()
    for var in config:
        ws_var = 'WEBSITE_%s' % var
        if hasattr(settings, ws_var):
            config[var] = getattr(settings, ws_var)
    return config


page_choices = get_config()

try:
    import django_bootstrap5.core as bootstrap
except ImportError:
    import bootstrap4.bootstrap as bootstrap

get_bootstrap_setting = bootstrap.get_bootstrap_setting
