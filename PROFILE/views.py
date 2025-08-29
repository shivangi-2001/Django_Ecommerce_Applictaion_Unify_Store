from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, UpdateView
from django_otp.plugins.otp_email.models import EmailDevice

from datetime import timedelta

from PROFILE.forms import UserRegistrationForm, UserAuthenticationLogin, UserUpdateFrom
from PROFILE.models import User


class Login(LoginView):
    form_class = UserAuthenticationLogin
    template_name = 'Profile/login.html'
    success_url = reverse_lazy('index')
    redirect_authenticated_user = True


class RegisterView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'Profile/registration.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.otp_attempts=3
        user.reset_time=None
        user.save()

        device, _ = EmailDevice.objects.get_or_create(user=user, name='default', email=user.email)
        device.generate_challenge()

        return redirect('verify_otp', pk=user.id)


class VerifyOTPView(View):
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user.is_active:
            return redirect("login")

        if user.reset_timer and user.reset_timer > timezone.now():
            messages.error(request, "Account locked. Try again later.")
            return redirect("create_user")

        return render(request, "Profile/verify_otp.html", {"user": user})

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        otp_code = request.POST.get("otp")

        if user.reset_timer and user.reset_timer > timezone.now():
            messages.error(request, "Account is locked. Try again later.")
            return redirect("create_user")

        device = EmailDevice.objects.filter(user=user, name="default").first()
        if not device:
            messages.error(request, "No OTP device found. Please register again.")
            return redirect("create_user")

        if device.verify_token(otp_code):
            user.is_active = True
            user.otp_attempts = 3
            user.reset_timer = None
            user.save()
            messages.success(request, "Account verified! Please login.")
            return redirect("login")
        else:
            user.otp_attempts -= 1
            if user.otp_attempts <= 0:
                user.reset_timer = timezone.now() + timezone.timedelta(minutes=30)
                user.is_active=False
                user.save()
                messages.error(request, "Too many attempts. Account locked for 30 minutes.")
                return redirect("create_user")

            user.save()
            messages.error(request, f"Invalid OTP. Attempts left: {user.otp_attempts}")
            return render(request, "Profile/verify_otp.html", {"user": user})


class VerifyAccount(View):
    def get(self, request):
        """
        If account exists but not yet verified → resend OTP.
        Reset attempts if lockout period expired.
        """
        user = get_object_or_404(User, email=request.GET.get('email'))

        # If already verified
        if user.is_active:
            return redirect("login")

        # Check lockout
        if user.reset_timer:
            if timezone.now() < user.reset_timer:
                # Still locked
                messages.error(request, "Your account is locked. Try again later.")
                return redirect("create_user")
            else:
                # Lock expired → reset attempts
                user.otp_attempts = 3
                user.reset_timer = None
                user.save()

        # Get or create EmailDevice for OTP
        device, created = EmailDevice.objects.get_or_create(user=user, name="default")

        # Resend OTP if not sent recently
        if not device.confirmed or device.last_t is None or timezone.now() > device.last_t + timedelta(minutes=2):
            device.generate_challenge()  # send OTP
            device.last_t = timezone.now()
            device.save()
            messages.info(request, "We have sent you a new OTP.")

        return render(request, "Profile/verify_otp.html", {"user": user})


class AccountProfile(UpdateView):
    model = User
    form_class = UserUpdateFrom
    template_name = 'Profile/profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user
