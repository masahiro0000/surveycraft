from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(label="ユーザー名", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ユーザー名'}))
    password = forms.CharField(label="パスワード", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'パスワード'}))

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(label="ユーザー名", widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "ユーザー名"}))
    password1 = forms.CharField(label="パスワード", widget=forms.PasswordInput(attrs={"class": "form-control"}))
    password2 = forms.CharField(label="パスワード確認用", widget=forms.PasswordInput(attrs={"class": "form-control"}))
    class Meta:
        model = get_user_model()
        fields = ("username", "password1", "password2")