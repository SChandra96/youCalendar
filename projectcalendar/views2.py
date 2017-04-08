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
	endTime = request.POST['endTime'] + ":00"
	new_event = Event(title=form.cleaned_data['title'],
					  startDate=startDate,
					  startTime=startTime,
					  endTime=endTime)
	new_event.save()
	new_event.admins.add(request.user)
	context['message'] = 'Your event has been saved to our calendar'
	UserWithFields.objects.get(user=request.user).events.add(new_event)
	#invite user by email, to edit event 
	
	return redirect('/')

@login_required
def checkEventPrivacy(request, id):
	event = get_object_or_404(Event, id=int(id))
	print request.user
	if request.user in event.admins.all():
		print event.admins.all()
		redirectUrl = '/edit_event/'+ id
		return redirect(redirectUrl)
	else:
		return redirect('/')

@login_required
def editEvent(request, id):
	context = {}

	if request.method == 'GET':
		eventObj = get_object_or_404(Event, id=int(id))
		context['form'] = EditEventForm({'title':eventObj.title, 
			'datepicker': eventObj.startDate })
		context['startTime'] = eventObj.startTime[:-3]
		context['endTime'] = eventObj.endTime[:-3]
		context['location'] = eventObj.location
		
		return render(request, 'projectCalendar/editEvent.html', context)

	form = EditEventForm(request.POST)
	if not form.is_valid():
		return render(request, 'projectCalendar/editEvent.html', context)

	event = get_object_or_404(Event, id=int(id))

	#if submitted form is repeat form:
	if 'repeat-form-flag' in request.POST:
		if(event.endTime == ""):
			print "line 63"
			context['error'] = 'Event must have an end time before set repeat!'
			return render(request, 'projectCalendar/editEvent.html', context)

		rangeStartDate =  request.POST['datepicker_st']
		rangeEndDate = request.POST['datepicker_end']
		repeatDate = []
		for j in range(1,8):
			ch_str = "repeat-date-"+str(j)
			if ch_str in request.POST:
				repeatDate.append(j%7)

		print "rangeStartDate: " + rangeStartDate
		print "rangeEndDate: " + rangeEndDate
		print "repeatDate: " + str(repeatDate)

		
		if(rangeStartDate < rangeEndDate):
			print "range date is valid!"
		else:
			context['error'] = 'EndDate must be later than StartDate!'
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
	whenToNotify = form.cleaned_data['notifTime']
	location = request.POST['location']
	print type(whenToNotify)
	notificationPref = request.POST['notifPref']
	
	if (startDate != ''): event.startDate = startDate
	if (title != ''): event.title = title
	if (startTime != ''): 
		if(len(startTime) >17):
			event.startTime = startTime
		else:
			event.startTime = startTime + ":00"
	if (endTime != ''): 
		if(startTime<endTime):
			if(len(endTime) >17):
				event.endTime = endTime
			else:
				event.endTime = endTime + ":00"
		else:
			context['error'] = 'End Time must be later than Start Time!'
			return render(request, 'projectCalendar/editEvent.html', context)

	if (whenToNotify and notificationPref != ''):
		event.whenToNotify = whenToNotify
		event.notificationPref = notificationPref
	if(location !=''):
		event.location = location
	event.save()
	context['message'] = 'Changes made to this event have been saved to our calendar'

	if (email != ''):
		selectOne = False
		try:
			inviteUser = User.objects.get(email=email)
			decUser = UserWithFields.objects.get(user=inviteUser)
		except:
			context['error'] = 'No user with email ID you entered exists'
			return render(request, 'projectCalendar/editEvent.html', context)
		
		if ("privacy-read" in request.POST and "privacy-r&w" not in request.POST):
			selectOne = True
			urlArgName = 'readOnly'
		
		elif ("privacy-read" not in request.POST and "privacy-r&w" in request.POST):
			selectOne = True
			urlArgName = 'readAndWrite'

		if selectOne:
			if event in decUser.events.all():
				context['error'] = "The user you are trying to share this event with already has read privileges"
			
			elif inviteUser in event.admins.all():
				context['error'] = "The user you are trying to share this event with already has read and write privileges"
			
			else:
				token = default_token_generator.make_token(inviteUser)
				email_url = "http://%s%s" % (request.get_host(), reverse(urlArgName, args=(event.title, email, token)))
				email_body = ("You've been invited to edit event " + event.title +
				 			 " Please click on the link below to be added to this event " + 
		                  	  email_url)
				print email_body
				send_mail(
						subject="Being added to an event",
					  	message= email_body,
					  	from_email="shikhaac@andrew.cmu.edu",
				  		recipient_list=[email])
				context['message'] += 'User has been invited to event ' + event.title + '.'
	
		else:
			context['error'] = "You must select the privacy level for the event. It must be either read only or read and write"
	
	return render(request, 'projectCalendar/editEvent.html', context)

@transaction.atomic
def acceptRead(request, eventTitle, userEmail, token):
    user = get_object_or_404(User, email=userEmail)
    decUser = UserWithFields.objects.get(user=user)
    event = get_object_or_404(Event, title=eventTitle)

    # Send 404 error if token is invalid
    if not default_token_generator.check_token(user, token):
        raise Http404

    decUser.events.add(event)
    decUser.save()
    return render(request, 'projectCalendar/acceptedInvitation.html', {})

@transaction.atomic
def acceptRW(request, eventTitle, userEmail, token):
    user = get_object_or_404(User, email=userEmail)
    decUser = UserWithFields.objects.get(user=user)
    event = get_object_or_404(Event, title=eventTitle)

    # Send 404 error if token is invalid
    if not default_token_generator.check_token(user, token):
        raise Http404

    decUser.events.add(event)
    decUser.save()
    event.admins.add(user)
    event.save()
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
			event_obj = {
			'title' : event.title, 'dow': DateList, 'start': start, 'end': end,'id': event.id,\
			'ranges':[{'r_start': event.rangeStartDate,\
			'r_end': event.rangeEndDate },],
			}
			
		else:
			event_obj = {'title' : event.title, 'start': start, 'end': end,
			'id': event.id,}
		if event.notificationPref and event.whenToNotify:
			event_obj['whenToNotify'] = event.whenToNotify
		 	event_obj['notificationPref'] = event.notificationPref
		if event.location:
			event_obj['location'] = event.location
		print event_obj			
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