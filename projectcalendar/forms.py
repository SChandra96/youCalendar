from django import forms
class CreateEventForm(forms.Form):
	title = forms.CharField(max_length=20)
	datepicker  = forms.CharField(max_length=20)

class EditEventForm(forms.Form):
	title = forms.CharField(max_length=20, required=False)
	datepicker  = forms.CharField(max_length=20, required=False)