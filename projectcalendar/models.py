from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Calendar(models.Model):
	name = models.CharField(max_length=20)
	
class Event(models.Model):
	title = models.CharField(max_length=20)
	startDate = models.CharField(max_length=10)
	startTime = models.CharField(max_length=20)
	endTime = models.CharField(max_length=10)
	DateList = models.TextField(null=True)
	rangeStartDate = models.CharField(max_length=10, null = True)
	rangeEndDate = models.CharField(max_length=10, null = True)
	whenToNotify = models.IntegerField(null = True)
	notificationPref = models.CharField(max_length=20, null=True)
	admins = models.ManyToManyField(User, related_name='admins')
	location = models.CharField(max_length = 100, null = True)
	isAppointment = models.BooleanField()
	apptSlot = models.IntegerField(null=True)
	apptCalendarUrl = models.CharField(max_length=100, null=True)
	token = models.CharField(max_length=10)
	calendar = models.ForeignKey(Calendar)

class AppointmentSlot(models.Model):
	token = models.CharField(max_length=10)
	event = models.ForeignKey(Event)
	#These are the only 2 fields which are different from the event's fields. (start time and end time)
	startTime = models.CharField(max_length=20)
	endTime = models.CharField(max_length=20)
	isBooked = models.BooleanField()
	user = models.ForeignKey(User, null=True)

class UserWithFields(models.Model):
	user = models.OneToOneField(User, related_name='user')
	events = models.ManyToManyField(Event)
	calendar = models.ManyToManyField(Calendar)


