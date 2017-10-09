from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns

from . import views


urlpatterns = [
	url(r'^teams/(?P<team_id>[0-9]+)/users/(?P<user_id>[0-9]+)/chats$', views.get_chats),
]

urlpatterns = format_suffix_patterns(urlpatterns)
