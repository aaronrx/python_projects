from django.conf.urls import url
from . import views

"""Defines URL patterns for learning_logs."""
app_name = 'learning_logs'

urlpatterns = [
    # url(<path>, <view()_to_call>, <name of url pattern>
    # Home page
    url(r'^$', views.index, name='index'),
    url(r'^topics/$', views.topics, name='topics'),

    # Match and store the integer in na argument called topic_id.
    # When Django finds a URL that matches this pattern, it calls the view
    # function topic() with the value stored in topic_id as an argument. We’ll use
    # the value of topic_id to get the correct topic inside the function.
    url(r'^topics/(?P<topic_id>\d+)/$', views.topic, name='topic'),

    # Page for adding a new topic
    url(r'^new_topic/$', views.new_topic, name='new_topic'),

    # Page for adding a new entry
    url(r'^new_entry/(?P<topic_id>\d+)/$', views.new_entry, name='new_entry'),

    # Page for editing an entry
    url(r'^edit_entry/(?P<entry_id>\d+)/$', views.edit_entry, name='edit_entry'),
]
