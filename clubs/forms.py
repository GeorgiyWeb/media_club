from django import forms
from .models import Club

class ClubCreateForm(forms.ModelForm):
    pick_title = forms.CharField(max_length=100, label="What are we discussing first?")
    pick_creator = forms.CharField(max_length=100, label="Who is the author?")
    
    class Meta:
        model = Club
        fields = ['name', 'description', 'category']