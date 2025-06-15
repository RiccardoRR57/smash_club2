from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group

class CreateBaseUser(UserCreationForm):
    # We override the save method to ensure the specified group
    # is assigned to the newly registered user. Groups can be created programmatically,
    # but in this case, we created them from the admin panel in the web interface.
    def save(self, commit=True):
        user = super().save(commit) # get a reference to the user
        g = Group.objects.get(name="players") # find the group of interest
        g.user_set.add(user) # add the user to the group
        return user # return what the parent method would have returned

class CreateTeacherUser(UserCreationForm):
    
    def save(self, commit=True):
        user = super().save(commit) 
        g = Group.objects.get(name="teachers") 
        g.user_set.add(user) 
        return user 
