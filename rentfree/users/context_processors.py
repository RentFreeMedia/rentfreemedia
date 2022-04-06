from django.conf import settings

def excluded_seo_views(request):

    return {'EXCLUDED_SEO_VIEWS': settings.EXCLUDED_SEO_VIEWS}
