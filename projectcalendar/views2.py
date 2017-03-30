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
from django.http import Http404
from django.contrib.auth.tokens import default_token_generator

# Used to send mail from within Django
from django.core.mail import send_mail
import pytz

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
	context['message'] = 'Your event has been saved to our calendar'
	UserWithFields.objects.get(user=request.user).events.add(new_event)
	#invite user by email, to edit event 
	
	return redirect('/')

@login_required
def editEvent(request, id):
	context = {}
	context['form'] = EditEventForm()
	if request.method == 'GET':
		return render(request, 'projectCalendar/editEvent.html', context)
	form = EditEventForm(request.POST)
	if not form.is_valid():
		return render(request, 'projectCalendar/editEvent.html', context)

	event = get_object_or_404(Event, id=int(id))

	print request.POST
	#if submitted form is repeat form:
	if 'repeat-form-flag' in request.POST:
		if(event.endTime == ""):
			print "line 63"
			context['message'] = 'Event must have an end time before set repeat!'
			return render(request, 'projectCalendar/editEvent.html', context)

		rangeStartDate =  request.POST['datepicker_st']
		rangeEndDate = request.POST['datepicker_end']
		repeatDate = []
		for j in range(1,8):
			ch_str = "repeat-date-"+str(j)
			if ch_str in request.POST:
				repeatDate.append(j)

		print "rangeStartDate: " + rangeStartDate
		print "rangeEndDate: " + rangeEndDate
		print "repeatDate: " + str(repeatDate)

		
		if(rangeStartDate < rangeEndDate):
			print "range date is valid!"
		else:
			context['message'] = 'EndDate must be later than StartDate!'
			return render(request, 'projectCalendar/editEvent.html', context)

		if(rangeStartDate != ''):
			event.rangeStartDate = rangeStartDate
		if(rangeEndDate != ''):
			event.rangeEndDate = rangeEndDate
		if(repeatDate != []):
			event.DateList = json.dumps(repeatDate)

		event.save()

		context['message'] = 'Changes made to this event have been saved to our calendar'
		return render(request, 'projectCalendar/editEvent.html', context)
	

	startDate = form.cleaned_data['datepicker']
	title = form.cleaned_data['title']
	startTime = request.POST['startTime']
	endTime = request.POST['endTime']
	email = form.cleaned_data['email']
	if (startDate != ''): event.startDate = startDate
	if (title != ''): event.title = title
	if (startTime != ''): event.startTime = startTime + ":00"
	if (endTime != ''): event.endTime = endTime + ":00"
	event.save()
	context['message'] = 'Changes made to this event have been saved to our calendar'
	if (email != ''):
		try:
			inviteUser = User.objects.get(email=email)
			token = default_token_generator.make_token(inviteUser)
			email_body = ("You've been invited to edit event " + event.title +
			 			 " Please click on the link below to be added to this event " + 
	                  	 "http://%s%s" % (request.get_host(), reverse('confirm', args=(event.title, email, token))))
			print email_body
			send_mail(
					subject="Being added to an event",
				  	message= email_body,
				  	from_email="shikhaac@andrew.cmu.edu",
			  		recipient_list=[email])
		except:
			context['message'] = 'No user with email ID you entered exists'
	
	return render(request, 'projectCalendar/editEvent.html', context)

@transaction.atomic
def inviteUserAccept(request, eventTitle, userEmail, token):
    user = get_object_or_404(User, email=userEmail)
    decUser = UserWithFields.objects.get(user=user)
    event = get_object_or_404(Event, title=eventTitle)

    # Send 404 error if token is invalid
    if not default_token_generator.check_token(user, token):
        raise Http404

    decUser.events.add(event)
    decUser.save()
    return render(request, 'projectCalendar/acceptedInvitation.html', {})


def get_list_json(request):
	events = []
	for event in UserWithFields.objects.get(user=request.user).events.all():
		start = event.startDate + 'T' + event.startTime 
		end = event.startDate + 'T' + event.endTime
		#
		#event.startDate + 'T' + 
		# {'title' : event.title, 'start': start, 'end': end,'id': event.id}
		jsonDec = json.decoder.JSONDecoder()
		if not event.DateList == None:
			DateList = jsonDec.decode(event.DateList)
			start = event.startTime 
			end = event.endTime
			
			# if(event.rangeStartDate == '') or (event.en)
			event_obj = {'title' : event.title, 'dow': DateList, 'start': start, 'end': end,'id': event.id,\
			'ranges':[{'r_start': event.rangeStartDate,\
			'r_end': event.rangeEndDate },]}
		else:
			event_obj = {'title' : event.title, 'start': start, 'end': end,
			'id': event.id,}
		

			
			
		events.append(event_obj)

	return HttpResponse(json.dumps(events), content_type='application/json')

def get_timezone_list():
	timezones = pytz.all_timezones
	
	return timezones

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
		print 'commin'
		context['message'] = 'Information input is invalid, please make sure that your username and email is unique.'
		return render(request, 'projectCalendar/register.html', context)

	# At this point, the form data is valid.  Register and login the user.
	new_user = User.objects.create_user(username=form.cleaned_data['username'], 
										password=form.cleaned_data['password1'],
										first_name=form.cleaned_data['first_name'],
										last_name=form.cleaned_data['last_name'],
										email=form.cleaned_data['email'])
	new_user.save()

	# Logs in the new user and redirects to his/her todo list
	new_user = authenticate(username=form.cleaned_data['username'],
							password=form.cleaned_data['password1'])
	new_user_with_fields = UserWithFields(user=new_user)
	new_user_with_fields.save()
	login(request, new_user)
	return redirect(reverse('home'))