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

    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label="Time",
        required=True,
    )

     # Add a field for inviting players
    invited_players = forms.ModelMultipleChoiceField(
        queryset=User.objects.exclude(is_superuser=True),  # Exclude admin users
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        label="Invite Players",
        required=False,
    )

    class Meta:
        model = Booking
        fields = ['court', 'start_time', 'invited_players']

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

    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label="Time",
        required=True,
    )

    until = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Repeat Until",
        required=True,
    )
    
    invited_players = forms.ModelMultipleChoiceField(
        queryset=User.objects.exclude(is_superuser=True).exclude(groups__name='teachers'),  # Exclude admin users
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        label="Invite Players",
        required=False,
    )

    class Meta:
        model = Booking
        fields = ['court', 'start_time', 'invited_players', 'until']

class CreateInvitationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        exclude_users = kwargs.pop('exclude_users', None)
        super().__init__(*args, **kwargs)
        if exclude_users:
            self.fields['user'].queryset = User.objects.exclude(id__in=[user.id for user in exclude_users])

    class Meta:
        model = InvitedPlayer
        fields = ['user']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
        }