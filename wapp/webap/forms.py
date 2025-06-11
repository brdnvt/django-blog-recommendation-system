from django import forms
from .models import PostComment
class BlogPostCreateForm(forms.Form):
    title = forms.CharField()
    text = forms.CharField(widget=forms.Textarea(attrs={"class": 'form-control', "rows": "10"}))
    post_picture = forms.ImageField(initial=None, required=False)
class BlogPostCommentForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(attrs={"class": 'form-control', "rows": "3"}))
    class Meta:
        model = PostComment
