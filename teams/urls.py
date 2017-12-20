from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns

from . import views
from locations import views as location_views 


urlpatterns = [
	url(r'^$', views.TeamList.as_view()),
	url(r'^(?P<team_id>[0-9]+)/$', views.TeamDetail.as_view()),
	url(r'^(?P<team_id>[0-9]+)/chats/$', views.get_chats),
	url(r'^(?P<team_id>[0-9]+)/status/$', views.TeamMembershipStatus.as_view()),
	url(r'^(?P<team_id>[0-9]+)/members/$', views.TeamMembershipList.as_view()),
	url(r'^(?P<team_id>[0-9]+)/members/(?P<user_id>[0-9]+)/$', views.TeamMemberDetail.as_view()),
	url(r'^(?P<team_id>[0-9]+)/checkins/$', views.CheckinList.as_view()),
	url(r'^(?P<team_id>[0-9]+)/checkins/(?P<checkin_id>[0-9]+)$', views.CheckinDetail.as_view()),
	url(r'^(?P<team_id>[0-9]+)/events/$', views.EventList.as_view()),
	url(r'^(?P<team_id>[0-9]+)/users/(?P<user_id>[0-9]+)/events/$', views.get_user_events),
	url(r'^(?P<team_id>[0-9]+)/users/(?P<user_id>[0-9]+)/locations/$', location_views.UserLocationList.as_view()),
    url(r'^(?P<team_id>[0-9]+)/media$', views.user_media_upload),
    url(r'^(?P<team_id>[0-9]+)/media/checkins$', views.checkin_media_upload),
	url(r'^(?P<team_id>[0-9]+)/subscriptions/$', location_views.LocationSubscriptionList.as_view()),
	url(r'^(?P<team_id>[0-9]+)/threads/(?P<thread_id>.+)$', views.MessagesList.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
