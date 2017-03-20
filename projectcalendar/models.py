from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Event(models.Model):
	title = models.CharField(max_length=20)
	start = models.CharField(max_length=160)