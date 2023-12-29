from django.contrib.auth.forms import AuthenticationForm, BaseUserCreationForm
from django import forms
from PROFILE.models import User

class UserAuthenticationLogin(AuthenticationForm):
    class Meta:
        model = User
        fields= ['email', 'password']
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