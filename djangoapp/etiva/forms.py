from django import forms

class ParticipantSearchForm(forms.Form):
    email = forms.EmailField(required=True)
    cpf = forms.CharField(max_length=14, required=True) 
