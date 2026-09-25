from django import forms
from .models import Club

class ClubCreateForm(forms.ModelForm):
    pick_title = forms.CharField(max_length=100)
    pick_creator = forms.CharField(max_length=100)
    
    class Meta:
        model = Club
        fields = ['name', 'description', 'category']