from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns

from . import views


urlpatterns = [
	url(r'^$', views.TeamList.as_view()),
	url(r'^(?P<team_id>[0-9]+)/$', views.TeamDetail.as_view()),
	url(r'^(?P<team_id>[0-9]+)/chats/$', views.get_chats),
	url(r'^(?P<team_id>[0-9]+)/status/$', views.TeamMembershipStatus.as_view()),
	url(r'^(?P<team_id>[0-9]+)/members/$', views.TeamMembershipList.as_view()),
	url(r'^[0-9]+/members/(?P<membership_id>[0-9]+)/$', views.TeamMembershipDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
