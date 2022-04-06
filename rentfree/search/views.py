from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib.contenttypes.models import ContentType
from django.db.models import F
from django.shortcuts import render
from wagtail.core.models import Site
from wagtail.search.backends import db, get_search_backend
from wagtail.search.models import Query
from wagtail_personalisation.models import PersonalisablePageMetadata
from website.forms import SearchForm
from website.models.pages import get_page_models, BasePage
from website.models.settings import GeneralSettings

def search(request):
    """
    Searches pages across the entire site.
    """
    search_form = SearchForm(request.GET)
    pagetypes = []
    results = None
    results_paginated = None
    site = Site.find_for_request(request)
    excluded_variant_pages = PersonalisablePageMetadata.objects.exclude(canonical_page_id=F('variant_id')).values_list('variant_id')

    if search_form.is_valid():
        search_query = search_form.cleaned_data['s']
        search_model = search_form.cleaned_data['t']

        # get all website models
        pagemodels = sorted(get_page_models(), key=lambda k: k.search_name)
        # get filterable models
        for model in pagemodels:
            if model.search_filterable:
                pagetypes.append(model)

        # get backend
        backend = get_search_backend()

        # DB search. Since this backend can't handle inheritance or scoring,
        # search specified page types in the desired order and chain the results together.
        # This provides better search results than simply searching limited fields on WebsitePage.
        db_models = []
        if backend.__class__ == db.SearchBackend:
            for model in get_page_models():
                if model.search_db_include:
                    db_models.append(model)
            db_models = sorted(db_models, reverse=True, key=lambda k: k.search_db_boost)

        if backend.__class__ == db.SearchBackend and db_models:
            for model in db_models:
                # if search_model is provided, only search on that model
                if not search_model or search_model == ContentType.objects.get_for_model(model).model:  # noqa
                    curr_results = model.objects.live().exclude(pk__in=excluded_variant_pages).search(search_query)
                    if results:
                        results = list(chain(results, curr_results))
                    else:
                        results = curr_results

        # Fallback for any other search backend
        else:
            if search_model:
                try:
                    model = ContentType.objects.get(model=search_model).model_class()
                    results = model.objects.live().exclude(pk__in=excluded_variant_pages).search(search_query)
                except search_model.DoesNotExist:
                    results = None
            else:
                results = BasePage.objects.live().exclude(pk__in=excluded_variant_pages).order_by('-last_published_at').search(search_query)  # noqa

        # paginate results
        if results:
            paginator = Paginator(results, GeneralSettings.for_request(request).search_num_results)
            page = request.GET.get('p', 1)
            try:
                results_paginated = paginator.page(page)
            except PageNotAnInteger:
                results_paginated = paginator.page(1)
            except EmptyPage:
                results_paginated = paginator.page(1)
            except InvalidPage:
                results_paginated = paginator.page(1)

        # Log the query so Wagtail can suggest promoted results
        Query.get(search_query).add_hit()

    # Render template
    return render(request, 'search/search.html', {
        'request': request,
        'pagetypes': pagetypes,
        'form': search_form,
        'results': results,
        'results_paginated': results_paginated
    })
