from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models

# Create your models here.
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
	
class UserWithFields(models.Model):
	user = models.OneToOneField(User, related_name='user')
	events = models.ManyToManyField(Event)

