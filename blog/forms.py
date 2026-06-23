from django import forms
from blog.models import Comment


class SubscribeForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'your@email.com', 'class': 'subscribe-input'})
    )


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['author_name', 'email', 'body']
        widgets = {
            'author_name': forms.TextInput(attrs={'placeholder': 'Your name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'your@email.com'}),
            'body': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Your comment...'}),
        }
