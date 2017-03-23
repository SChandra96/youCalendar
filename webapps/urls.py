from django.contrib import admin
from django.conf.urls import include, url
from projectcalendar import views2 as views

urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    url(r'^$', views.home,name = 'home'),
    url(r'^projectcalendar/', include('projectcalendar.urls')),
   
]
