from django.urls import include, re_path
from . import cud_views, views

urlpatterns_catalog = [
    re_path(r'^$', views.catalog, name='catalog'),
    re_path(r'^create/$', views.create_medication, name='med_create'),
    re_path(r'^edit/(?P<pk>\d+)/$', views.edit_medication, name='med_edit'),
    re_path(r'^delete/(?P<pk>\d+)/$', views.delete_medication, name='med_delete'),
    re_path(r'^categories/$', views.category_list, name='category_list'),
    re_path(r'^categories/create/$', cud_views.categorymedication_create, name='category_create'),
    re_path(r'^categories/edit/(?P<pk>\d+)/$', cud_views.categorymedication_update, name='category_edit'),
    re_path(r'^categories/delete/(?P<pk>\d+)/$', cud_views.categorymedication_delete, name='category_delete'),
]

urlpatterns_employees = [
    re_path(r'^$', views.employee_list, name='employee_list'),
    re_path(r'^create/$', cud_views.employee_create, name='employee_create'),
    re_path(r'^edit/(?P<pk>\d+)/$', cud_views.employee_update, name='employee_edit'),
    re_path(r'^delete/(?P<pk>\d+)/$', cud_views.employee_delete, name='employee_delete'),
    re_path(r'^departments/$', views.department_list, name='department_list'),
    re_path(r'^departments/create/$', cud_views.department_create, name='department_create'),
    re_path(r'^departments/edit/(?P<pk>\d+)/$', cud_views.department_update, name='department_edit'),
    re_path(r'^departments/delete/(?P<pk>\d+)/$', cud_views.department_delete, name='department_delete'),
]

urlpatterns_other = [
    re_path(r'^admin_suppliers/$', views.supplier_list, name='supplier_list'),
    re_path(r'^admin_sales/$', views.sale_list, name='sale_list'),
    re_path(r'^admin_sale-items/$', views.saleitem_list, name='saleitem_list'),
    re_path(r'^admin_benefits/$', views.benefits_list, name='benefits_list'),
    re_path(r'^admin_coupons/$', views.coupons_list, name='coupons_list'),
    re_path(r'^admin_vacancies/$', views.vacancy_list, name='vacancy_list'),
    re_path(r'^admin_suppliers/create/$', cud_views.supplier_create, name='supplier_create'),
    re_path(r'^admin_suppliers/edit/(?P<pk>\d+)/$', cud_views.supplier_update, name='supplier_edit'),
    re_path(r'^admin_suppliers/delete/(?P<pk>\d+)/$', cud_views.supplier_delete, name='supplier_delete'),
    re_path(r'^admin_sales/create/$', cud_views.sale_create, name='sale_create'),
    re_path(r'^admin_sales/edit/(?P<pk>\d+)/$', cud_views.sale_update, name='sale_edit'),
    re_path(r'^admin_sales/delete/(?P<pk>\d+)/$', cud_views.sale_delete, name='sale_delete'),
    re_path(r'^admin_saleitem/create/$', cud_views.saleitem_create, name='saleitem_create'),
    re_path(r'^admin_saleitem/edit/(?P<pk>\d+)/$', cud_views.saleitem_update, name='saleitem_edit'),
    re_path(r'^admin_saleitem/delete/(?P<pk>\d+)/$', cud_views.saleitem_delete, name='saleitem_delete'),
    re_path(r'^admin_benefits/create/$', cud_views.benefits_create, name='benefits_create'),
    re_path(r'^admin_benefits/edit/(?P<pk>\d+)/$', cud_views.benefits_update, name='benefits_edit'),
    re_path(r'^admin_benefits/delete/(?P<pk>\d+)/$', cud_views.benefits_delete, name='benefits_delete'),
    re_path(r'^admin_coupons/create/$', cud_views.coupons_create, name='coupons_create'),
    re_path(r'^admin_coupons/edit/(?P<pk>\d+)/$', cud_views.coupons_update, name='coupons_edit'),
    re_path(r'^admin_coupons/delete/(?P<pk>\d+)/$', cud_views.coupons_delete, name='coupons_delete'),
    re_path(r'^admin_vacancy/create/$', cud_views.vacancy_create, name='vacancy_create'),
    re_path(r'^admin_vacancy/edit/(?P<pk>\d+)/$', cud_views.vacancy_update, name='vacancy_edit'),
    re_path(r'^admin_vacancy/delete/(?P<pk>\d+)/$', cud_views.vacancy_delete, name='vacancy_delete'),
    re_path(r'^users/$', views.user_management, name='user_management'),
]

urlpatterns = [
    re_path(r'^catalog/', include(urlpatterns_catalog)),
    re_path(r'^employees/', include(urlpatterns_employees)),
    re_path(r'^management/', include(urlpatterns_other)),
    re_path(r'^contacts/$', views.contacts, name='contacts'),
    re_path(r'^promo/$', views.promo, name='promo'),
    re_path(r'^vacancies/$', views.vacancies, name='vacancies'),
    re_path(r'^login/$', views.login_view, name='login_view'),
    re_path(r'^shop/', include('shop.urls')),
]
