from django import forms

class SignUpForm(forms.Form):
    username = forms.CharField(label="Username", widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Username'}))
    email = forms.CharField(label="Email (optional)", widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Email'}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'}))
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':''}))

class LogInForm(forms.Form):
    username = forms.CharField(label="Username", widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Enter username'}))
    password = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Enter password'}))
