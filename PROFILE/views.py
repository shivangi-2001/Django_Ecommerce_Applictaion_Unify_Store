from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, FormView, UpdateView, ListView
from django_otp.plugins.otp_email.models import EmailDevice
from django.conf import settings
import datetime
from PROFILE.forms import UserRegistrationForm, OTPVerificationForm, UserAuthenticationLogin, UserUpdateFrom
from PROFILE.models import User


class Login(LoginView):
    form_class = UserAuthenticationLogin
    template_name = 'Profile/login.html'
    success_url = reverse_lazy('index')


class RegisterView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'Profile/registration.html'

    def get_success_url(self):
        device = EmailDevice.objects.create(user_id=self.object.id, name='Email')
        device.generate_challenge({'email':self.object})
        return reverse_lazy('verify_otp', kwargs={'pk': self.object.id})


class VerifyOTPView(View):
    def get(self, request, pk):
        current_user = User.objects.get(id=pk)
        if current_user.is_active:
            return redirect('index')
        else:
            # if user is not blocked for 30 minutes
            if current_user.reset_timer is None or timezone.now() > current_user.reset_timer:
                device = EmailDevice.objects.get(user_id=pk)
                if device.token:
                    if device.valid_until > timezone.now():
                        print("Token is not  expired ")
                        return render(request, 'Profile/verify_otp.html', {'login_attempt': settings.OTP_LOGIN_ATTEMPT})
                    else:
                        info = "Sending the OTP to verify your account again Because your OTP is expired ..."
                        device.generate_challenge({'email': current_user})
                        return render(request, 'Profile/verify_otp.html', context={'info': info, 'login_attempt': settings.OTP_LOGIN_ATTEMPT})
            else:
                error_message = f"Your Account ${current_user} is locked, Try Again After sometimes"
                return redirect( 'create_user')


    def post(self, request, pk):
        otp = request.POST.get('otp')
        current_time = timezone.now()

        if otp:
            form = OTPVerificationForm(request.POST)
            if form.is_valid():
                entered_otp = form.cleaned_data['otp']
                device = EmailDevice.objects.get(user_id=pk)
                user = User.objects.get(id=pk)

                if (user.reset_timer and user.reset_timer > timezone.now()) or (
                        device.last_generated_timestamp < current_time < device.valid_until):
                    verified = device.verify_token(token=entered_otp)

                    if verified:
                        active_account = User.objects.get(id=pk)
                        active_account.is_active = True
                        active_account.reset_time = None
                        active_account.save()
                        return redirect('profile', pk=pk)
                    else:
                        if settings.OTP_LOGIN_ATTEMPT > 1:
                            settings.OTP_LOGIN_ATTEMPT -= 1
                            error_message = "Incorrect OTP. Try Again"
                            return render(request, template_name='Profile/verify_otp.html',
                                          context={'error_message': error_message, 'login_attempt': settings.OTP_LOGIN_ATTEMPT})
                        else:
                            error_message = "Try Again after 30 minutes"
                            user_email = User.objects.get(id=pk)
                            user_email.reset_timer = timezone.now() + datetime.timedelta(minutes=settings.EMAIL_RESET_TIME)
                            user_email.save()
                            return render(request, 'Profile/registration.html', context={'error_message': error_message})
                else:
                    info = "Sending the OTP to verify your account again Because your OTP is expired ..."
                    device.generate_challenge({'email': User.objects.get(id=pk)})
                    settings.OTP_LOGIN_ATTEMPT = 3
                    return render(request, 'Profile/verify_otp.html', context={'info': info, 'login_attempt': settings.OTP_LOGIN_ATTEMPT})
            else:
                return HttpResponse("Something Went Wrong Sending the OTP Again ... ")
        else:
            error_message = "Enter the OTP.... "
            return render(request, template_name='Profile/verify_otp.html', context={'error_message': error_message, 'login_attempt': settings.OTP_LOGIN_ATTEMPT})

class AccountProfile(UpdateView):
    model = User
    template_name = 'Profile/profile.html'
    form_class = UserUpdateFrom

def get_user_id(request):
    if request.method == 'POST':
        email_input = request.POST.get('email')
        try:
            user = get_object_or_404(User, email=email_input)
            user_id = user.id
            return redirect('verify_otp', pk=user_id)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)