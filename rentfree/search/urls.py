from django.urls import re_path
from search.views import search

urlpatterns = [
    re_path(r'', search, name='website_search'),
]