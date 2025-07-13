from django import forms
from .models import CustomUser, Post

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'profile_pic', 'bio']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user




class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image']

        