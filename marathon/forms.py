'''
Created on 27 Aug 2014

@author: rxv
'''

from django import forms
from django.contrib.auth.forms import UserCreationForm
from marathon.models import ContactRegistration, Event
from django.contrib.auth.models import User

class UserForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    has_read_t_and_cs = forms.BooleanField(required=True, label="I have read and I agree to the Terms and Conditions", error_messages={'required': 'You must agree with the Terms and Conditions to register'})

class CustomLoginForm(forms.Form):
    email_or_username = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Username or email"}), required=True, label="Username or email")
    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder":"Password"}), required=True, label="Password" )
    
    def clean(self):
        cleaned_data = super(CustomLoginForm, self).clean()
        email_or_username = cleaned_data.get("email_or_username")
        try:
            user = User.objects.get(username=email_or_username)
        except:
            try:
                user = User.objects.get(email=email_or_username)
            except:
                raise forms.ValidationError("User unknown")
        cleaned_data["user"] = user
        if not user.check_password(cleaned_data.get("password")):
            raise forms.ValidationError("Incorrect password")
        return cleaned_data

class ContactRegistrationForm(forms.ModelForm):
    class Meta:
        model = ContactRegistration
        fields = ['email']
        widgets = {'email': forms.EmailInput(attrs={'placeholder': 'Enter your email address to know more'})}

class RunnerSearchForm(forms.Form):
    event = forms.ModelChoiceField(queryset = Event.objects.filter(public=True), initial=Event.objects.get(is_current=True), required=True, error_messages={'required': 'Please choose an event'})
    runner_number = forms.IntegerField(required=True, min_value=1, error_messages={'required': 'Please enter a runner number'})    
    def __init__(self, reqget, requser, *args, **kwargs):
        super(RunnerSearchForm, self).__init__(reqget, *args, **kwargs)
        if requser.is_superuser:
            self.fields["event"].queryset = Event.objects.all()