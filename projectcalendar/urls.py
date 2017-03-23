from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from projectcalendar import views2 as projectcalendar_views

urlpatterns = [
    url(r'^$', projectcalendar_views.home, name='home'),
    # url(r'^global_stream$', projectcalendar_views.global_stream, name='global_stream'),
    # url(r'^create$', projectcalendar_views.create, name='create'),
    # url(r'^profile$', projectcalendar_views.profile, name='profile'),
    # url(r'^edit/(\d+)$', projectcalendar_views.edit, name='edit'),
    url(r'^add_event$', projectcalendar_views.displayEventForm, name='add_event'),
    url(r'^edit_event/(\d+)$', projectcalendar_views.editEvent, name='edit_event'),
    url(r'^get-list-json$', projectcalendar_views.get_list_json),
    url(r'^register$', projectcalendar_views.register, name='register'),
    # # Route for built-in authentication with our own custom login page
    url(r'^login$', auth_views.login, {'template_name':'projectcalendar/login.html'}, name='login'),
    # # Route to logout a user and send them back to the login page
    url(r'^logout$', auth_views.logout_then_login, name='logout'),
]

