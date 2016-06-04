from django.conf.urls import patterns, url

urlpatterns = patterns(
    'spc.views',
    #url(r'^performs/(?P<tester_name>\w+)/$', 'perform_detail', name='perform_detail'),
    url(r'^xml/$', 'xml_transaction', name='xml_transaction'),
    url(r'^performs/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]{2})/(?P<type>\w+)/$',
        'perform_tracking', name='perform_tracking'),
    url(r'^performs/(?P<perform_id>\w+)/$', 'perform_detail', name='perform_detail'),
    url(r'^performs/(?P<perform_id>\w+)/actions/$', 'perform_actions', name='perform_actions'),
    url(r'^performs/(?P<perform_id>\w+)/(?P<param_name>\w+)/(?P<action_details>[\w ]+)/$',
        'perform_action_update', name='perform_action_update'),
    url(r'^setting/parameter/$', 'param_setting_detail', name='param_setting_detail'),
    url(r'^performs/check/(?P<tester_name>\w+)/$', 'tester_ready', name='tester_ready'),
    url(r'^performs/get/(?P<tester_name>\w+)/$', 'last_failed_spc', name='last_failed_spc'),
   )

