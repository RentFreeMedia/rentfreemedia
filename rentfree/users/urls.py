from django.urls import include, path, re_path
from users import views
from wagtailcache.cache import nocache_page

urlpatterns = [
    path('unsubscribe/<uidb64>/<token>/', nocache_page(views.UnsubscribeView.as_view()), name='unsubscribe'),
    re_path(r'^profile/', nocache_page(views.newuser_switch_view(views.InitialProfileView.as_view(), views.SubsequentProfileView.as_view())), name='profile'),
    re_path(r'', include('allauth_2fa.urls')),
]
