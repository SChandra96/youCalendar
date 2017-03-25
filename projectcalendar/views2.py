from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from projectcalendar.forms import *
from projectcalendar.models import *
from django.http import HttpResponse
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.db import transaction
import json

# Create your views here.
@login_required
def home(request):
	context = {}
	context['form'] = CreateEventForm()
	return render(request, 'projectCalendar/index2.html', context)

@login_required
def addEvent(request):
	context = {}
	context['form'] = CreateEventForm()
	if request.method == 'GET':
		return render(request, 'projectCalendar/index2.html', context)
	form = CreateEventForm(request.POST)
	if not form.is_valid():
		return render(request, 'projectCalendar/index2.html', context)
	startDate = form.cleaned_data['datepicker']
	startTime = request.POST['startTime']+":00"
	new_event = Event(title=form.cleaned_data['title'],
					  startDate=startDate,
					  startTime=startTime)
	new_event.save()
	UserWithFields.objects.get(user=request.user).events.add(new_event)
	context['message'] = 'Your event has been saved to our calendar'
	return redirect('/')

@login_required
def editEvent(request, id):
	context = {}
	print id
	context['form'] = EditEventForm()
	if request.method == 'GET':
		print 'hello'
		return render(request, 'projectCalendar/editEvent.html', context)
	form = EditEventForm(request.POST)
	if not form.is_valid():
		return render(request, 'projectCalendar/editEvent.html', context)
	event = get_object_or_404(Event, id=int(id))
	startDate = form.cleaned_data['datepicker']
	title = form.cleaned_data['title']
	startTime = request.POST['startTime']
	if (startDate != ''): event.startDate = startDate
	if (title != ''): event.title = title
	if (startTime != ''): event.startTime = startTime + ":00"
	event.save()
	context['message'] = 'Changes made to this event have been saved to our calendar'
	return render(request, 'projectCalendar/editEvent.html', context)


def get_list_json(request):
	events = []
	for event in UserWithFields.objects.get(user=request.user).events.all():
		start = event.startDate + 'T' + event.startTime 
		print event.id
		events.append({'title' : event.title, 'start': start, 'id': event.id})
	return HttpResponse(json.dumps(events), content_type='application/json')

@transaction.atomic
def register(request):
	context = {}

	# Just display the registration form if this is a GET request.
	if request.method == 'GET':
		context['form'] = RegistrationForm()
		return render(request, 'projectCalendar/register.html', context)

	# Creates a bound form from the request POST parameters and makes the 
	# form available in the request context dictionary.
	form = RegistrationForm(request.POST)
	context['form'] = form

	# Validates the form.
	if not form.is_valid():
		return render(request, 'projectCalendar/register.html', context)

	# At this point, the form data is valid.  Register and login the user.
	new_user = User.objects.create_user(username=form.cleaned_data['username'], 
										password=form.cleaned_data['password1'],
										first_name=form.cleaned_data['first_name'],
										last_name=form.cleaned_data['last_name'])
	new_user.save()

	# Logs in the new user and redirects to his/her todo list
	new_user = authenticate(username=form.cleaned_data['username'],
							password=form.cleaned_data['password1'])
	new_user_with_fields = UserWithFields(user=new_user)
	new_user_with_fields.save()
	login(request, new_user)
	return redirect(reverse('home'))