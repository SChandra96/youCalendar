from django.shortcuts import render, redirect, get_object_or_404
from projectcalendar.forms import *
from projectcalendar.models import *
from django.http import HttpResponse
from django.core import serializers
import json
# Create your views here.
def home(request):
    context = {}
    context['form'] = CreateEventForm()
    return render(request, 'projectCalendar/index.html', context)

def displayEventForm(request):
	context = {}
	context['form'] = CreateEventForm()
	if request.method == 'GET':
		return render(request, 'projectCalendar/addEvent.html', context)
	form = CreateEventForm(request.POST)
	if not form.is_valid():
	    return render(request, 'projectCalendar/addEvent.html', context)
	start = form.cleaned_data['datepicker']
	print start
	new_event = Event(title=form.cleaned_data['title'],
					  start=start)
	new_event.save()
	context['message'] = 'Your event has been saved to our calendar'
	return render(request, 'projectCalendar/addEvent.html', context)

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