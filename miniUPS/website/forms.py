from re import A
from django import forms
from website.models import Package


class RegisterForm(forms.Form):
    username = forms.CharField(label='Username', required=True, widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    email = forms.CharField(label='Email', required=True, widget=forms.EmailInput(
        attrs={'class': 'form-control'}))
    password = forms.CharField(label='Password', required=True,
                               widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Repeat your password', required=True,
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class LoginForm(forms.Form):
    username = forms.CharField(label='Username', required=True, widget=forms.TextInput(
        attrs={'class': 'form-control form-control-lg', 'placeholder': 'Enter your user name'}))
    password = forms.CharField(label='Password', required=True, widget=forms.PasswordInput(
        attrs={'class': 'form-control form-control-lg', 'placeholder': 'Enter password'}))


class TrackForm(forms.Form):
    trackingid = forms.IntegerField(
        label='Tracking_id', required=True, widget=forms.NumberInput(attrs={'class': 'form-control'}))

    def clean_trackingid(self):
        trackingid = self.cleaned_data.get('trakingid')
        filter_result = Package.objects.filter(tracking_id=trackingid)
        if len(filter_result) <= 0:
            raise forms.ValidationError(
                "The tracking number you entered is not valid.")
