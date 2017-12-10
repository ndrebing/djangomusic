from django import forms

class AddItemForm(forms.Form):
    link = forms.CharField(label='Link', max_length=100)

class AddConfigForm(forms.Form):
    shuffle = forms.BooleanField(label = 'Shuffle', initial=False)
    repeat = forms.BooleanField(label = 'Repeat', initial=False)
