from django.urls import re_path
from . import views

app_name = "stats_graf"

urlpatterns = [
    re_path(r'^$', views.stats_view, name='stats'),
]
