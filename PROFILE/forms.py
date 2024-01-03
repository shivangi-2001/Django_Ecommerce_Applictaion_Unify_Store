from django.contrib.auth.forms import AuthenticationForm, BaseUserCreationForm
from django import forms
from PROFILE.models import User
from django_otp.plugins.otp_email.models import EmailDevice

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
        fields = ['email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=True)
        if commit:
            user.save()
            # call send otp()
        return user

class OTPVerificationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['otp']


class UserUpdateFrom(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']