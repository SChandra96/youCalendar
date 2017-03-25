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
    url(r'^get-list-json$', views.get_list_json),
    url(r'^register$', views.register, name='register'),
    # # Route for built-in authentication with our own custom login page
    url(r'^login$', auth_views.login, {'template_name':'projectcalendar/login.html'}, name='login'),
    # # Route to logout a user and send them back to the login page
    url(r'^logout$', auth_views.logout_then_login, name='logout'),
]
