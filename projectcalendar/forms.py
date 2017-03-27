from django import forms
from django.contrib.auth.models import User
from models import *


class CreateEventForm(forms.Form):
	title = forms.CharField(max_length=20)
	datepicker  = forms.CharField(max_length=20)
	
class EditEventForm(forms.Form):
	title = forms.CharField(max_length=20, required=False)
	datepicker  = forms.CharField(max_length=20, required=False)
	email = forms.CharField(max_length=50, widget = forms.EmailInput(), required=False)
	
class RegistrationForm(forms.Form):
	first_name = forms.CharField(max_length=20)
	last_name  = forms.CharField(max_length=20)
	username   = forms.CharField(max_length = 20)
	password1  = forms.CharField(max_length = 200, 
								 label='Password', 
								 widget = forms.PasswordInput())
	password2  = forms.CharField(max_length = 200, 
								 label='Confirm password',  
								 widget = forms.PasswordInput())
	email = forms.CharField(max_length=50,
							widget = forms.EmailInput())


	# Customizes form validation for properties that apply to more
	# than one field.  Overrides the forms.Form.clean function.
	def clean(self):
		# Calls our parent (forms.Form) .clean function, gets a dictionary
		# of cleaned data as a result
		cleaned_data = super(RegistrationForm, self).clean()

		# Confirms that the two password fields match
		password1 = cleaned_data.get('password1')
		password2 = cleaned_data.get('password2')
		if password1 and password2 and password1 != password2:
			raise forms.ValidationError("Passwords did not match.")

		# We must return the cleaned data we got from our parent.
		return cleaned_data


	# Customizes form validation for the username field.
	def clean_username(self):
		# Confirms that the username is not already present in the
		# User model database.
		username = self.cleaned_data.get('username')
		if User.objects.filter(username__exact=username):
			raise forms.ValidationError("Username is already taken.")

		# We must return the cleaned data we got from the cleaned_data
		# dictionary
		return username

	def clean_email(self):
		email = self.cleaned_data.get('email')
		if User.objects.filter(email__exact=email):
			raise forms.ValidationError("Email is already taken.")

		# We must return the cleaned data we got from the cleaned_data
		# dictionary
		return email