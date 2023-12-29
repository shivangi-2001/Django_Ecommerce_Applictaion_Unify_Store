from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView
from django_otp.plugins.otp_email.models import EmailDevice

from PROFILE.forms import UserRegistrationForm, OTPVerificationForm, UserAuthenticationLogin
from PROFILE.models import User


class Login(LoginView):
    form_class = UserAuthenticationLogin
    template_name = 'Profile/login.html'
    success_url = reverse_lazy('home_page')

class RegisterView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'Profile/registration.html'

    def get_success_url(self):
        device = EmailDevice.objects.create(user_id=self.object.id, name='Email')
        device.generate_challenge({'email':self.object})
        return reverse_lazy('verify_otp', kwargs={'pk': self.object.id})


class VerifyOTPView(FormView):
    template_name = 'Profile/verify_otp.html'
    form_class = OTPVerificationForm

    def form_valid(self, form):
        user_id = self.kwargs['pk']
        user = User.objects.get(id=user_id)
        otp_entered = form.cleaned_data['otp']

        # Validate OTP and check expiration time
        device = EmailDevice.objects.get(user_id=user.id)
        verified = device.verify_token(otp_entered)

        if verified:
            user.email_verified = True
            user.is_active = True  # Activate the account upon successful OTP verification
            user.save()
            # Set permissions or any other action for activating the account
            return HttpResponse('Account activated successfully!')
        else:
            return HttpResponse('Invalid OTP or OTP expired. Please try again.')
