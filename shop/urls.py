from django.urls import re_path
from . import views

app_name = "shop"

urlpatterns = [
    re_path(r'^profile/$', views.profile_view, name='profile'),
    re_path(r'^cart/$', views.cart_view, name='cart'),
    re_path(r'^cart/add/(?P<pk>\d+)/$', views.add_to_cart, name='add_to_cart'),
    re_path(r'^cart/item/(?P<item_id>\d+)/add/$', views.cart_item_add, name='cart_item_plus'),
    re_path(r'^cart/item/(?P<item_id>\d+)/notadd/$', views.cart_item_notadd, name='cart_item_minus'),
    re_path(r'^cart/item/(?P<item_id>\d+)/delete/$', views.cart_item_delete, name='cart_item_delete'),
    re_path(r'^cart/checkout/$', views.checkout, name='checkout'),
    re_path(r'^orders/process/$', views.orders_to_process, name='orders_to_process'),
    re_path(r'^orders/approve/(?P<order_id>\d+)/$', views.approve_order, name='approve_order'),
    re_path(r'^orders/history/$', views.order_history, name='order_history'),
    re_path(r'^orders/(?P<order_id>\d+)/$', views.order_detail, name='order_detail'),
    re_path(r'^orders/(?P<order_id>\d+)/cancel/$', views.cancel_order, name='cancel_order'),
]