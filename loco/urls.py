"""loco URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from accounts import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
]

#API urls
urlpatterns += [
    url(r'^users/', include('accounts.urls')),
    url(r'^teams/', include('teams.urls')),
    url(r'^sapi/', include('morty.urls')),
    url(r'^locations/', include('locations.urls')),
    url(r'^groups/', include('groups.urls')),
    url(r'^events', views.UserDumpView.as_view()),
    url(r'^download', views.get_download_link),
]


if settings.DEBUG:
    urlpatterns = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + urlpatterns