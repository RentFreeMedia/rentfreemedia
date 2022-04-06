from django.conf import settings
from django.urls import include, path, re_path
from django.contrib import admin
from payments import urls as payment_urls
from search import urls as search_urls
from users import urls as users_urls
from allauth import urls as allauth_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from website.models.choices import page_choices
from website.views import (
    favicon,
    robots,
    PremiumMediaView
)

if 'debug_toolbar' in settings.INSTALLED_APPS and settings.DEBUG:
    import debug_toolbar
    from django.conf.urls.static import static
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns = []

urlpatterns += [

    re_path(r'^favicon\.ico$', favicon, name='website_favicon'),
    re_path(r'^robots\.txt$', robots, name='website_robots'),
    re_path(r'^sitemap\.xml$', sitemap, name='website_sitemap'),

    # Django admin
    path('django-admin/', admin.site.urls),

    # Wagtail admin
    path('admin/', include(wagtailadmin_urls)),

    # Wagtail documents
    path('documents/', include(wagtaildocs_urls)),

    # Search results
    path('search/', include(search_urls)),

    # Summernote editor
    path('summernote/', include('django_summernote.urls')),

    path('comment/', include('comment.urls')),

    # Stripe payments
    re_path(r'', include(payment_urls)),

    # Django-Allauth user accounts
    re_path(r'', include(allauth_urls)),

    #User profile urls
    re_path(r'', include(users_urls)),

    re_path(r'^premium_media/(?P<uidb64>[-\w]*)/(?P<fileid>[-\w]*)/(?P<token>[-\w]*)/(?P<file_name>[\w.]{0,256})$', PremiumMediaView.as_view(), name='premium_media'),

]

urlpatterns += [
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path('', include(wagtail_urls)),

    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    path("pages/", include(wagtail_urls)),
]
