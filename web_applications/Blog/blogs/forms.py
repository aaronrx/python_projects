from django import forms
from .models import BlogPost


class BlogPostForm(forms.ModelForm):
    class Meta:
        """A Form class based on the model BlogPost"""
        model = BlogPost
        fields = ['text']
        labels = {'text': ''}
        widgets = {'text': forms.Textarea(attrs={'cols': 80})}
