from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns

from . import views


urlpatterns = [
	url(r'^teams/(?P<team_id>[0-9]+)/users/(?P<user_id>[0-9]+)/chats$', views.get_chats),
	url(r'^locations$', views.set_user_location),
	url(r'^attendance$', views.set_user_attendance),
	url(r'^messages$', views.add_or_update_message)
]

urlpatterns = format_suffix_patterns(urlpatterns)
