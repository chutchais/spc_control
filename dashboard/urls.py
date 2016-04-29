from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^GH/(?P<operation_name>[-\w|\W\ ]+)/(?P<model_name>[-\w|\W\ ]+)/(?P<date_from_in>[-\w|\W\ ]+)/(?P<date_to_in>[-\w|\W\ ]+)/(?P<group_by>[-\w|\W\ ]+)/(?P<parameter>[-\w|\W\ ]+)/(?P<tester>[-\w|\W\ ]+)/$',
        views.graph_histogram, name='histogram'),
    url(r'^GHM/(?P<operation_name>[-\w|\W\ ]+)/(?P<model_name>[-\w|\W\ ]+)/(?P<date_from_in>[-\w|\W\ ]+)/(?P<date_to_in>[-\w|\W\ ]+)/(?P<group_by>[-\w|\W\ ]+)/(?P<parameter>[-\w|\W\ ]+)/(?P<tester>[-\w|\W\ ]+)/$',
        views.graph_hist_all_model, name='histogram_all'),
    url(r'^GBB/(?P<operation_name>[-\w|\W\ ]+)/(?P<model_name>[-\w|\W\ ]+)/(?P<date_from_in>[-\w|\W\ ]+)/(?P<date_to_in>[-\w|\W\ ]+)/(?P<group_by>[-\w|\W\ ]+)/(?P<parameter>[-\w|\W\ ]+)/(?P<tester>[-\w|\W\ ]+)/$',
        views.graph_boxplot, name='boxplot'),
    url(r'^GP/(?P<operation_name>[-\w|\W\ ]+)/(?P<model_name>[-\w|\W\ ]+)/(?P<date_from_in>[-\w|\W\ ]+)/(?P<date_to_in>[-\w|\W\ ]+)/(?P<group_by>[-\w|\W\ ]+)/(?P<parameter>[-\w|\W\ ]+)/(?P<tester>[-\w|\W\ ]+)/$',
        views.graph_boxplot, name='productiongraph'),
    url(r'^unit_track/$', views.form_unit_tracking, name='unittrack'),
    url(r'^Q/$', views.form_oper_query, name='operform'),
    url(r'^O/(?P<operation_name>[-\w|\W\ ]+)/(?P<model_name>[-\w|\W\ ]+)/(?P<date_from_in>[-\w|\W\ ]+)/(?P<date_to_in>[-\w|\W\ ]+)/(?P<group_by>[-\w|\W\ ]+)/(?P<parameter>[-\w|\W\ ]+)/(?P<tester>[-\w|\W\ ]+)/$',
        views.view_query_oper_model,name='query_by_oper_model'),
    url(r'^Q/(?P<operation_name>[-\w|\W\ ]+)/(?P<date_from_in>[-\w|\W\ ]+)/(?P<date_to_in>[-\w|\W\ ]+)/$', views.view_query_oper_main, name='mainquery'),
    url(r'^perform/(?P<perform_id>\w+)/(?P<perform_type>\w+)$', views.view_perform_detail, name='view_perform_detail'),
    url(r'^perform/(?P<tester_name>[-\w|\W\ ]+)/(?P<param_name>[-\w|\W\ ]+)/(?P<rule_name>\w+)/(?P<side>\w+)/(?P<perform_type>\w+)$',
        views.view_param_detail, name='view_param_detail'),
    url(r'^actions/(?P<perform_id>\w+)/$', views.set_actions, name='set_actions'),
    url(r'^perform/(?P<tester_name>[-\w|\W\ ]+)/(?P<param_name>[-\w|\W\ ]+)/(?P<perform_type>[-\w|\W\ ]+)$',
        views.view_chart_detail, name='view_chart_detail'),
    url(r'^graph/(?P<tester_name>[-\w|\W\ ]+)/(?P<param_name>[-\w|\W\ ]+)/(?P<model>[-\w|\W\ ]+)/(?P<side>\w+)/$',views.graphsviewbar, name='graph'),
]
