from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns

from . import views


urlpatterns = [
	url(r'^$', views.new_user_maps),
	url(r'^raw', views.raw_user_maps),
]

urlpatterns = format_suffix_patterns(urlpatterns)
