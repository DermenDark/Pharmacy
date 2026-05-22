from django.urls import re_path, include
from . import views, cud_views

urlpatterns_public = [
    re_path(r'^$', views.index, name='about_company'),
    re_path(r'^news/$', views.news, name='news'),
    re_path(r'^news/(?P<pk>\d+)/$', views.news_detail, name='news_detail'),
    re_path(r'^reviews/$', views.reviews, name='reviews'),
    re_path(r'^terms/$', views.terms, name='terms'),
    re_path(r'^politic/$', views.politic, name='politic'),
]

urlpatterns_admin = [
    re_path(r'^admin_company/$', views.index, name='admin_about_company'),
    re_path(r'^admin_news/$', cud_views.admin_news, name='admin_news'),
    re_path(r'^admin_reviews/$', cud_views.admin_reviews, name='admin_reviews'),
    re_path(r'^admin_terms/$', cud_views.admin_terms, name='admin_terms'),
]

urlpatterns = [
    re_path(r'^', include(urlpatterns_public)),
    re_path(r'^', include(urlpatterns_admin)),

    re_path(r'^company/create/$', cud_views.about_company_create, name='about_company_create'),
    re_path(r'^company/edit/(?P<pk>\d+)/$', cud_views.about_company_edit, name='about_company_edit'),
    re_path(r'^company/delete/(?P<pk>\d+)/$', cud_views.about_company_delete, name='about_company_delete'),

    re_path(r'^news/create/$', cud_views.news_create, name='news_create'),
    re_path(r'^news/edit/(?P<pk>\d+)/$', cud_views.news_edit, name='news_edit'),
    re_path(r'^news/delete/(?P<pk>\d+)/$', cud_views.news_delete, name='news_delete'),

    re_path(r'^reviews/create/$', cud_views.review_create, name='review_create'),
    re_path(r'^reviews/edit/(?P<pk>\d+)/$', cud_views.review_edit, name='review_edit'),
    re_path(r'^reviews/delete/(?P<pk>\d+)/$', cud_views.review_delete, name='review_delete'),

    re_path(r'^terms/create/$', cud_views.term_create, name='term_create'),
    re_path(r'^terms/edit/(?P<pk>\d+)/$', cud_views.term_edit, name='term_edit'),
    re_path(r'^terms/delete/(?P<pk>\d+)/$', cud_views.term_delete, name='term_delete'),
]