from django.conf.urls import url
from . import views

"""Defines URL patterns for pizzeria."""
app_name = 'pizzas'

urlpatterns = [
    # url(<path>, <view()_to_call>, <name of url pattern>
    # Home page
    url(r'^$', views.index, name='index'),
    url(r'^menu/$', views.menu, name='menu'),
    url(r'^pizza/(?P<pizza_id>\d+)/$', views.pizza, name='pizza'),
]
