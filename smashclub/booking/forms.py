from django import forms
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.utils import timezone
from datetime import datetime, timedelta
from .models import *

class CreateBookingForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        court = cleaned_data.get('court')
        date = cleaned_data.get('date')
        hour = cleaned_data.get('hour')
        
        if court and date and hour:
            # Create the datetime for the booking
            naive_start_time = datetime.combine(date, datetime.min.time()).replace(hour=int(hour))
            start_time = timezone.make_aware(naive_start_time)
            
            # Check if slot is already booked
            if Booking.objects.filter(court=court, start_time=start_time).exists():
                raise forms.ValidationError('This time slot is already booked.')
                
            # Additional validations
            now = timezone.now()
            if start_time < now:
                raise forms.ValidationError('Cannot book slots in the past.')
                
            if not (8 <= int(hour) <= 21):
                raise forms.ValidationError('Bookings are only available between 08:00 and 21:00.')
                
            # Check 7-day advance booking rule
            if self.user and not (self.user.groups.filter(name='teachers').exists() or self.user.is_staff):
                if start_time > now + timedelta(days=7):
                    raise forms.ValidationError('Regular users can only book up to 7 days in advance.')
        
        return cleaned_data

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

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        court = cleaned_data.get('court')
        date = cleaned_data.get('date')
        hour = cleaned_data.get('hour')
        
        if court and date and hour:
            # Create the datetime for the booking
            naive_start_time = datetime.combine(date, datetime.min.time()).replace(hour=int(hour))
            start_time = timezone.make_aware(naive_start_time)
            
            if not (8 <= int(hour) <= 21):
                raise forms.ValidationError('Bookings are only available between 08:00 and 21:00.')
                
            # Additional validations
            now = timezone.now()
            if start_time < now:
                raise forms.ValidationError('Cannot book slots in the past.')
                
            # Check if slot is already booked
            if Booking.objects.filter(court=court, start_time=start_time).exists():
                raise forms.ValidationError('This time slot is already booked.')
                
            # Check 7-day advance booking rule
            if self.user and not (self.user.groups.filter(name='teachers').exists() or self.user.is_staff):
                if start_time > now + timedelta(days=7):
                    raise forms.ValidationError('Regular users can only book up to 7 days in advance.')
        
        return cleaned_data

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