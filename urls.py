from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.views import login, logout_then_login

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'jpardy.views.home', name='home'),
    # url(r'^jpardy/', include('jpardy.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'apps.jpardy.views.home'),
    url(r'^home/$', 'apps.jpardy.views.home'),
    url(r'^edit/(\d+)/$', 'apps.jpardy.views.edit'),

    url(r'^login/$', login),
    url(r'^logout/$', logout_then_login),
)
