from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns

from . import views


urlpatterns = [
	url(r'^(?P<group_id>[0-9]+)/$', views.GroupDetail.as_view()),
	url(r'^(?P<group_id>[0-9]+)/members/$', views.GroupMembershipList.as_view()),
	url(r'^(?P<group_id>[0-9]+)/members/(?P<membership_id>[0-9]+)/$', views.GroupMembershipDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
