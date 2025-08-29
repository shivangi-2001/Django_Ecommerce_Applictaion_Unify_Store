from django.contrib.auth.forms import AuthenticationForm, BaseUserCreationForm
from django import forms
from django.contrib.auth.forms import SetPasswordForm

from PROFILE.models import User


class UserAuthenticationLogin(AuthenticationForm):
    username = forms.EmailField(
        error_messages={'required': 'This field is required', 'invalid': 'This field is case sensitive'},
        widget=forms.EmailInput(attrs={'type': 'email','class': 'form-control form-control-md', 'placeholder': 'email@domain.com', 'autocomplete': 'off'}),
        label='Email',
        max_length=254,
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-md', 'placeholder': 'password', 'autocomplete': 'off'}),
        label="Password"
    )

class UserRegistrationForm(BaseUserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user


class UserUpdateFrom(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name',  'email']

class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        label="Enter your registered email",
        widget=forms.EmailInput(attrs={'class':'form-control', 'placeholder':'email@domain.com'})
    )

class SetPassword(SetPasswordForm):
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password', 'autocomplete': 'off'}),
        strip=False,
    )
    new_password2 = forms.CharField(
        label="Confirm new password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm New Password', 'autocomplete': 'off'}),
        strip=False,
    )

    info_text = "Your password must contain at least 8 characters and should not be entirely numeric."
