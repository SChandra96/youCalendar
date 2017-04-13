from django.contrib import admin
from django.conf.urls import include, url
from projectcalendar import views2 as views
from django.contrib.auth import views as auth_views

# urlpatterns = [
#     # url(r'^admin/', admin.site.urls),
#     url(r'^$', views.home, name="home"),
#     url(r'^projectcalendar/', include('projectcalendar.urls')),
   
# ]

urlpatterns = [
    url(r'^$', views.home, name = 'home'),
    url(r'^add_event$', views.addEvent, name='add_event'),
    url(r'^edit_event/(\d+)$', views.editEvent, name='edit_event'),
    url(r'^book_appt/(?P<token>[a-z0-9\-]+)/(?P<id>[0-9\-]+)$', views.bookAppointment, name='book_appt'),
    url(r'^check_event_privacy/(\d+)$', views.checkEventPrivacy),
    url(r'^delete_event/(\d+)$',views.deleteEvent),
    url(r'^get-list-json$', views.get_list_json),
    url(r'^get-appt-list-json/(?P<token>[a-z0-9\-]+)$', views.get_appt_list_json),
    # url(r'^get-timezone-json$', views.get_timezone_list),
    url(r'^register$', views.register, name='register'),
    # # Route for built-in authentication with our own custom login page
    url(r'^login$', auth_views.login, {'template_name':'projectcalendar/login.html'}, name='login'),
    # # Route to logout a user and send them back to the login page
    url(r'^logout$', auth_views.logout_then_login, name='logout'),
    url(r'^acceptReadInvitation/(?P<eventTitle>[a-zA-Z0-9_@\+\-]+)/(?P<userEmail>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/(?P<token>[a-z0-9\-]+)$',
        views.acceptRead, name='readOnly'),
    url(r'^acceptReadAndWriteInvitation/(?P<eventTitle>[a-zA-Z0-9_@\+\-]+)/(?P<userEmail>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/(?P<token>[a-z0-9\-]+)$',
        views.acceptRW, name='readAndWrite'),
    url(r'^appointmentCalendar/(?P<token>[a-z0-9\-]+)$', views.seeAptCalendar, name='apptCalendar'),
]
