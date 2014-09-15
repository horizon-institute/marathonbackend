'''
Created on 27 Aug 2014

@author: rxv
'''

from django import forms
from django.contrib.auth.forms import UserCreationForm
from marathon.models import ContactRegistration

class UserForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    has_read_t_and_cs = forms.BooleanField(required=True, label="I have read and I agree to the Terms and Conditions", error_messages={'required': 'You must agree with the Terms and Conditions to register'})

class ContactRegistrationForm(forms.ModelForm):
    
    class Meta:
        model = ContactRegistration
        fields = ['email']