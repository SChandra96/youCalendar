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
def displayEventForm(request):
	context = {}
	context['form'] = CreateEventForm()
	if request.method == 'GET':
		return render(request, 'projectCalendar/index2.html', context)
	form = CreateEventForm(request.POST)
	if not form.is_valid():
	    return render(request, 'projectCalendar/index2.html', context)
	start = form.cleaned_data['datepicker']+'T'+request.POST['startTime']+":00"
	print start
	new_event = Event(title=form.cleaned_data['title'],
					  start=start)
	new_event.save()
	print'new event'
	context['message'] = 'Your event has been saved to our calendar'
	return redirect('/')

@login_required
def editEvent(request, id):
	context = {}
	print id
	context['form'] = EditEventForm()
	if request.method == 'GET':
		print 'hello'
		return render(request, 'projectCalendar/addEvent.html', context)
	form = EditEventForm(request.POST)
	if not form.is_valid():
	    return render(request, 'projectCalendar/addEvent.html', context)
	event = get_object_or_404(Event, id=int(id))
	print event
	start = form.cleaned_data['datepicker']
	title = form.cleaned_data['title']
	if (start != ''): event.start = start
	if (title != ''): event.title = title
	event.save()
	context['message'] = 'Changes made to this event have been saved to our calendar'
	return render(request, 'projectCalendar/addEvent.html', context)

def get_list_json(request):
	print 'hello'
	events = []
	for event in Event.objects.all():
		events.append({'title' : event.title, 'start': event.start})
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
	login(request, new_user)
	return redirect(reverse('home'))