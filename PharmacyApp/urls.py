from django.conf import settings
from django.views.static import serve
from django.contrib import admin
from django.urls import include, re_path
from django.contrib.auth import views as auth_views

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^stats/', include('stats_graf.urls')),
    re_path(r'^logout/$', auth_views.LogoutView.as_view(next_page='about_company'), name='logout'),
    re_path(r'^', include('pharmacy.urls')),
    re_path(r'^', include('info.urls')),
]
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]