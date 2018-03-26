from django import forms
from django.forms import FileInput, DateInput
from .models import Place

class NewPlaceForm(forms.ModelForm):
    class Meta:
        model = Place
        fields = ('name', 'visited')


# http://stackoverflow.com/questions/28213682/create-type-date-in-django-form
class DateInput(forms.DateInput):
    input_type = 'date'  # Override the default input type, which is 'text'. 

class TripReviewForm(forms.ModelForm):
    class Meta:
        model = Place
        fields = ('notes', 'date_visited', 'photo')
        widgets = {
            'date_visited': DateInput()
        }
