from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns

from . import views


urlpatterns = [
	url(r'^getOtp$', views.getOtp, name="auth-get-otp"),
	url(r'^login', views.login_user, name='auth-login'),
	url(r'^logout', views.logout_user, name='auth-logout'),
	url(r'^me$', views.UserMeDetail.as_view(), name='user-me'),
	url(r'^dump2$', views.UserDumpView2.as_view(), name='user-dump1'),
	url(r'^dump21$', views.UserDumpJsonP2.as_view(), name='user-dump1'),
	url(r'^maps$', views.user_maps, name='user-dump1'),
	url(r'^me/gcm$', views.UpdateGCMToken.as_view(), name='update-gcm-token'),
    url(r'^pings$', views.user_pings, name = 'user_phone'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
