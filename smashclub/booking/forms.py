from django import forms
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import *

class CreateBookingForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_id = "addbooking_crispy_form"
    helper.form_method = "POST"
    helper.add_input(Submit("submit","Add Booking", css_class="btn btn-primary"))
    helper.form_class = "form-horizontal"

    court = forms.ModelChoiceField(
        queryset=Court.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Court",
        required=True,
    )

    HOURS_CHOICES = [(hour, f"{hour}:00") for hour in range(8, 22)]  # Hours from 08:00 to 21:00

    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Start Date",
        required=True,
    )

    hour = forms.ChoiceField(
        choices=HOURS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Start Hour",
        required=True,
    )

    class Meta:
        model = Booking
        fields = ['court', 'date', 'hour']

class RecurringBookingForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_id = "recurring_booking_crispy_form"
    helper.form_method = "POST"
    helper.add_input(Submit("submit", "Create Recurring Booking", css_class="btn btn-primary"))
    helper.form_class = "form-horizontal"

    court = forms.ModelChoiceField(
        queryset=Court.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Court",
        required=True,
    )

    HOURS_CHOICES = [(hour, f"{hour}:00") for hour in range(8, 22)]  # Hours from 08:00 to 21:00

    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Start Date",
        required=True,
    )

    hour = forms.ChoiceField(
        choices=HOURS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Start Hour",
        required=True,
    )

    until = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Repeat Until",
        required=True,
    )
    class Meta:
        model = Booking
        fields = ['court', 'date', 'hour', 'until']

class CreateCourtForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_id = "add_court_crispy_form"
    helper.form_method = "POST"
    helper.add_input(Submit("submit", "Add Court", css_class="btn btn-primary"))
    helper.form_class = "form-horizontal"

    class Meta:
        model = Court
        fields = ['name','surface', 'description', 'is_active', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'surface': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

class AssignTeacherForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(groups__name='players').exclude(groups__name='teachers'),
        label="Select User",
        widget=forms.Select(attrs={'class': 'form-control'})
    )