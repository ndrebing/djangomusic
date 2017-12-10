from django import forms

class SignUpForm(forms.Form):
    username = forms.CharField(label='username', max_length=100)
    passwort = forms.CharField(label='passwort', max_length=100)
