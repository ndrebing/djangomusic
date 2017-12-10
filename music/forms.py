from django import forms

class AddItemForm(forms.Form):
    link = forms.CharField(label='Link', max_length=100)
