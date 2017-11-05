from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns

from . import views


urlpatterns = [
	url(r'^getOtp$', views.getOtp),
	url(r'^login', views.login_user),
	url(r'^logout', views.logout_user),
	url(r'^me$', views.UserMeDetail.as_view()),
	url(r'^me/gcm$', views.UpdateGCMToken.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
