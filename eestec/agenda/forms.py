from django import forms

class AgendaForm(forms.Form):
    date=forms.DateField()
    lc=forms.CharField(max_length=50)
