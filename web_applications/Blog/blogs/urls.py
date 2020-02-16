from django.conf.urls import url
from . import views

"""Defines URL patterns for the Blog."""
app_name = 'blogs'

urlpatterns = [
    # url(<path>, <view()_to_call>, <name of url pattern>
    # Home page
    url(r'^$', views.index, name='index'),

    # Page for creating new post
    url(r'^new_post$', views.new_post, name='new_post'),

    # Page for editing post
    url(r'^edit_post/(?P<blogpost_id>\d+)/$', views.edit_post, name='edit_post'),
]
