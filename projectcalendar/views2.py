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
from django.utils.crypto import get_random_string

# Used to send mail from within Django
from django.core.mail import send_mail
import string
import random 
from datetime import datetime, timedelta

# Create your views here.
@login_required
def home(request):
	context = getCalendarNames(request.user)
	context['form'] = CreateEventForm()
	error = request.session.pop('error', False)
	if error:
		context['error'] = error
	return render(request, 'projectcalendar/index2.html', context)

def createNewAppointmentSlots(event, token, startDate):
	fmt = "%Y-%m-%d%H:%M:%S"
	startTime = datetime.strptime(startDate + event.startTime, fmt)
	endTime = datetime.strptime(startDate + event.endTime, fmt)
	slotDuration= event.apptSlot
	numberOfSlots = ((endTime-startTime).seconds/60)/slotDuration
	print numberOfSlots
	for i in xrange(1, numberOfSlots+1):
		apptStartTime = (startTime + timedelta(minutes=slotDuration*(i-1))).time()
		apptStartTimeDB = startDate + "T" + apptStartTime.strftime("%H:%M:%S")
		apptEndTime = (startTime + timedelta(minutes=slotDuration*i)).time()
		apptEndTimeDB = startDate + "T" + apptEndTime.strftime("%H:%M:%S")
		newAppt = AppointmentSlot(event=event,
							  token=token, 
							  startTime=apptStartTimeDB, 
							  endTime=apptEndTimeDB, 
							  isBooked=False)
		newAppt.save()

def recreateAppointmentSlots(rangeStartDate, rangeEndDate, dateList, event):
	AppointmentSlot.objects.all().filter(token=event.token).delete()
	fmt = "%Y-%m-%d"
	startDate = datetime.strptime(rangeStartDate, fmt)
	endDate = datetime.strptime(rangeEndDate, fmt)
	numberOfDays = (endDate-startDate).days
	for i in xrange(numberOfDays+1):
		curDate = startDate + timedelta(days=i)
		print curDate.strftime(fmt)
		if ((curDate.weekday()+1)%7) in dateList:
			createNewAppointmentSlots(event, event.token, curDate.strftime(fmt))


@login_required
def bookAppointment(request, token, id):
	appt = get_object_or_404(AppointmentSlot, id=int(id))
	appt.isBooked = True
	appt.user = request.user
	appt.save()
	return redirect('/appointmentCalendar/'+token)

def getCalendarNames(user):
	decUser = get_object_or_404(UserWithFields, user=user)
	context = {'calNames': []}
	for calendar in decUser.calendar.all():
		context['calNames'].append(calendar.name)
	return context

def validateEventDetails(startTime, endTime, isAppt, apptSlot, eventTitle, decoratedUser, calendarName):
	fmt = "%H:%M:%S"
	start = datetime.strptime(startTime, fmt)
	end = datetime.strptime(endTime, fmt)
	if end <= start:
		return "End time of event must be after start time. Please try again"
	if isAppt ^ apptSlot:
		return "To create an appointment, you must set type of event to appointment and enter a slot duration. Try again"
	if len(decoratedUser.events.all().filter(title=eventTitle)) > 0:
		return "Please create an event with a unique name"
	if calendarName == '':
		return "You must create a calendar before adding an event to it"
	return ""

@login_required
def addEvent(request):
	context = getCalendarNames(request.user)
	context['form'] = CreateEventForm()
	if request.method == 'GET':
		return render(request, 'projectcalendar/index2.html', context)
	form = CreateEventForm(request.POST)
	if not form.is_valid():
		return redirect('/')

	decUser = UserWithFields.objects.get(user=request.user)
	if 'calName' in request.POST:	
		calendarName = request.POST['calName']
		calendar = decUser.calendar.get(name=calendarName)
	else: calendarName = ''
	title = form.cleaned_data['title']
	startDate = form.cleaned_data['datepicker']
	startTime = request.POST['startTime']+":00"
	endTime = request.POST['endTime'] + ":00"
	isAppointment = "appointment" in request.POST and "appointmentSlot" in request.POST
	error = validateEventDetails(startTime, endTime, "appointment" in request.POST,
								"appointmentSlot" in request.POST, title, decUser, calendarName)
	if error != '':
		request.session['error'] = error
		return redirect('/')

	new_event = Event(title=form.cleaned_data['title'],
					  startDate=startDate,
					  startTime=startTime,
					  endTime=endTime, isAppointment=isAppointment, calendar=calendar)
	new_event.save()
	if isAppointment:
		if not "slotTime" in request.POST:
			request.session['error'] = "You must enter a slot duration to create an appointment"
			return redirect('/')
		new_event.apptSlot = int(request.POST["slotTime"])
		token = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
		new_event.token = token
		new_event.save()
		createNewAppointmentSlots(new_event, token, startDate)
		apptCalendarUrl = "http://%s%s" % (request.get_host(), reverse("apptCalendar", args=[token]))
		print apptCalendarUrl
		new_event.apptCalendarUrl = apptCalendarUrl
		new_event.save()
	
	new_event.admins.add(request.user)
	context['message'] = 'Your event has been saved to our calendar'
	UserWithFields.objects.get(user=request.user).events.add(new_event)
	#invite user by email, to edit event 
	
	return redirect('/')

@login_required
def createCalendar(request):
	if request.method == 'POST':
		name = request.POST['calendarName']
		decUser = get_object_or_404(UserWithFields.objects, user=request.user)
		if len(decUser.calendar.all().filter(name=name)) > 0:
			request.session['error'] = 'Calendar names must be distinct. Please try again'
			return redirect('/')
		new_calendar = Calendar(name=name)
		new_calendar.save()
		decUser.calendar.add(new_calendar)
		decUser.save()
		return redirect('/')


def seeAptCalendar(request, token):
	if request.user.is_authenticated:
		return render(request, 'projectcalendar/appointmentCalendar.html', {})
	else:
		return redirect('/login')

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

def deleteEvent(request,id):
	event = get_object_or_404(Event, id=int(id))
	print request.user
	if request.user in event.admins.all():
		print event.admins.all()
		event.delete();
		return redirect('/')
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
		
		return render(request, 'projectcalendar/editEvent.html', context)
	context['form'] = EditEventForm()
	form = EditEventForm(request.POST)

	if not form.is_valid():
		return render(request, 'projectcalendar/editEvent.html', context)

	event = get_object_or_404(Event, id=int(id))
	eventObj = get_object_or_404(Event, id=int(id))
	context['form'] = EditEventForm({'title':eventObj.title, 
		'datepicker': eventObj.startDate })
	context['startTime'] = eventObj.startTime[:-3]
	context['endTime'] = eventObj.endTime[:-3]
	context['location'] = eventObj.location
	#if submitted form is repeat form:
	if 'repeat-form-flag' in request.POST:
		if(event.endTime == ""):
			print "line 63"
			context['error'] = 'Event must have an end time before set repeat!'
			return render(request, 'projectcalendar/editEvent.html', context)

		rangeStartDate =  request.POST['datepicker_st']
		rangeEndDate = request.POST['datepicker_end']
		repeatDate = []
		for j in range(1,8):
			ch_str = "repeat-date-"+str(j)
			if ch_str in request.POST:
				repeatDate.append(j%7)
		dateList = json.dumps(repeatDate)
		print "rangeStartDate: " + rangeStartDate
		print "rangeEndDate: " + rangeEndDate
		print "repeatDate: " + str(repeatDate)

		
		if(rangeStartDate < rangeEndDate):
			print "range date is valid!"
		else:
			context['error'] = 'EndDate must be later than StartDate!'
			return render(request, 'projectcalendar/editEvent.html', context)

		event.save()
		if(rangeStartDate != '' and rangeEndDate != '' and repeatDate != []):
			event.rangeStartDate = rangeStartDate
			event.rangeEndDate = rangeEndDate
			event.DateList = dateList
			event.save()
			print event
			if event.isAppointment:
				recreateAppointmentSlots(rangeStartDate, rangeEndDate, repeatDate, event)

		context['message'] = 'Changes made to this event have been saved to our calendar'
		return render(request, 'projectcalendar/editEvent.html', context)
	

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

			return render(request, 'projectcalendar/editEvent.html', context)

	if (whenToNotify and notificationPref != ''):
		event.whenToNotify = whenToNotify
		event.notificationPref = notificationPref
	if(location !=''):
		event.location = location
	event.save()
	context['message'] = 'Changes made to this event have been saved to our calendar'
	if not 'repeat-form-flag' in request.POST:
		if event.isAppointment:
			print "one time"
			AppointmentSlot.objects.all().filter(token=event.token).delete()
			createNewAppointmentSlots(event, event.token, event.startDate)

	if (email != ''):
		selectOne = False
		try:
			inviteUser = User.objects.get(email=email)
			decUser = UserWithFields.objects.get(user=inviteUser)
		except:
			context['error'] = 'No user with email ID you entered exists'
			return render(request, 'projectcalendar/editEvent.html', context)
		
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
				# token = default_token_generator.make_token(inviteUser)
				token = get_random_string(length=32)
				print "line 309 : "+ token

				if(EM_Token.objects.filter(em_user=inviteUser, em_event=event).count() == 0):
					new_token_record = EM_Token(em_user=inviteUser, em_event=event,em_token=token)
					new_token_record.save()
				else:
					old_token_record = EM_Token.objects.get(em_user=inviteUser, em_event=event)
					token = old_token_record.em_token
				
				email_url = "http://%s%s" % (request.get_host(), reverse(urlArgName, args=(event.title, email, token)))
				email_body = ("You've been invited to the event " + event.title +
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
	
	eventObj = get_object_or_404(Event, id=int(id))
	context['form'] = EditEventForm({'title':eventObj.title, 
		'datepicker': eventObj.startDate })
	context['startTime'] = eventObj.startTime[:-3]
	context['endTime'] = eventObj.endTime[:-3]
	context['location'] = eventObj.location

	return render(request, 'projectcalendar/editEvent.html', context)

@transaction.atomic
def acceptRead(request, eventTitle, userEmail, token):
	
	user = get_object_or_404(User, email=userEmail)
	decUser = UserWithFields.objects.get(user=user)
	event = get_object_or_404(Event, title=eventTitle)
	print  eventTitle, userEmail, token
	# Send 404 error if token is invalid
	# if not default_token_generator.check_token(user, token):
	# EM_Token.objects.filter(em_user=user, em_event=event,em_token=token).exists
	if(not EM_Token.objects.filter(em_user=user, em_event=event,em_token=token).count() == 1):
		raise Http404
	else:
		instance = EM_Token.objects.get(em_user=user, em_event=event,em_token=token)
		print "line 349"
		print instance
		instance.delete()

	decUser.events.add(event)
	decUser.save()
 
	return render(request, 'projectcalendar/acceptedInvitation.html', {})
	

@transaction.atomic
def acceptRW(request, eventTitle, userEmail, token):
	user = get_object_or_404(User, email=userEmail)
	decUser = UserWithFields.objects.get(user=user)
	event = get_object_or_404(Event, title=eventTitle)

	# Send 404 error if token is invalid
	# if not default_token_generator.check_token(user, token):
	if(not EM_Token.objects.filter(em_user=user, em_event=event, em_token=token).count() == 1):
		raise Http404

	decUser.events.add(event)
	decUser.save()
	event.admins.add(user)
	event.save()

	return render(request, 'projectcalendar/acceptedInvitation.html', {})

def makeEventList(qs):
	events = []
	for event in qs:
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
		if event.isAppointment: 
			event_obj['apptEvent'] = True
			event_obj['apptURL'] = event.apptCalendarUrl
		print event_obj			
		events.append(event_obj)
	return events

def makeAppointmentList(qs, color, adminView):
	appointments = []
	for appointment in qs:
		appointment_obj = {'title' : appointment.event.title, 'start': appointment.startTime, 'end': appointment.endTime,
				'id': appointment.id, 'isBooked': appointment.isBooked or adminView, 'color': color, 
				'isApptSlot': True}
		if appointment.isBooked:
			appointment_obj['color'] = 'green'
		appointments.append(appointment_obj)
	print appointments
	return appointments

def get_cal_specific_evtList(request, calNames):
	calendarNames = calNames.split(",")
	calEvents = []
	myAppointmentSlots = []
	decuser = UserWithFields.objects.get(user=request.user)
	userEventsQS = decuser.events.all()
	#get all events on calendars owned by user.
	for calName in calendarNames:
		calendar = decuser.calendar.get(name=calName)
		qs = userEventsQS.filter(calendar=calendar)
		calEvents+= makeEventList(qs)
		apptEvents = qs.filter(isAppointment=True)
		for apptEvent in apptEvents:
			qs3 = AppointmentSlot.objects.all().filter(event=apptEvent)
			myAppointmentSlots += makeAppointmentList(qs3, "grey", False)
	events = calEvents + myAppointmentSlots
	return HttpResponse(json.dumps(events), content_type='application/json')

def get_list_json(request):
	qs = UserWithFields.objects.get(user=request.user).events.all()
	qs2 = AppointmentSlot.objects.all().filter(user=request.user) #appt slots i signed up for
	myAppointmentSlots = [] #appt slots created by me
	apptEvents = qs.filter(isAppointment=True)
	for apptEvent in apptEvents:
		qs3 = AppointmentSlot.objects.all().filter(event=apptEvent)
		myAppointmentSlots += makeAppointmentList(qs3, "grey", False)
	events = makeEventList(qs) + makeAppointmentList(qs2, "blue", False) + myAppointmentSlots
	return HttpResponse(json.dumps(events), content_type='application/json')

def get_appt_list_json(request, token):
	print request.user
	qs = AppointmentSlot.objects.all().filter(token=token)
	corrospondingEvent = Event.objects.all().get(token=token)
	decUser = UserWithFields.objects.all().get(user=request.user)
	print request.user, corrospondingEvent.admins.all()
	adminView = request.user in corrospondingEvent.admins.all()
	events = makeAppointmentList(qs, "blue", adminView)
	return HttpResponse(json.dumps(events), content_type='application/json')

@transaction.atomic
def register(request):
	context = {}

	# Just display the registration form if this is a GET request.
	if request.method == 'GET':
		context['form'] = RegistrationForm()
		return render(request, 'projectcalendar/register.html', context)

	# Creates a bound form from the request POST parameters and makes the 
	# form available in the request context dictionary.
	form = RegistrationForm(request.POST)
	context['form'] = form

	# Validates the form.
	if not form.is_valid():
		print 'commin'
		context['message'] = 'Information input is invalid, please make sure that your username and email is unique.'
		return render(request, 'projectcalendar/register.html', context)

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