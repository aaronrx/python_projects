from django import forms
from .models import Topic, Entry


class TopicForm(forms.ModelForm):
    class Meta:
        """A Form class based on the model Topic"""
        model = Topic
        fields = ['text']
        labels = {'text': ''}


class EntryForm(forms.ModelForm):
    class Meta:
        """A Form class based on the model Entry"""
        model = Entry
        fields = ['text']
        labels = {'text': ''}
        widgets = {'text': forms.Textarea(attrs={'cols': 80})}
