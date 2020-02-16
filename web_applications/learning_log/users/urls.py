from django.conf.urls import url
from django.contrib.auth.views import LoginView
from . import views

"""Defines URL patterns for users."""
app_name = 'users'

urlpatterns = [
    # url(<path>, <view()_to_call>, <name of url pattern>
    # Login page
    url(r'^login/$', LoginView.as_view(template_name='users/login.html'), name='login'),

    # Logout page
    url(r'^logout/$', views.logout_view, name='logout_view'),

    # Registration Page
    url(r'^register/$', views.register, name='register'),
]
