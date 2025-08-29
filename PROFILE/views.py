from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, UpdateView
from django_otp.plugins.otp_email.models import EmailDevice

from datetime import timedelta
from urllib.parse import quote

from PROFILE.forms import UserRegistrationForm, UserAuthenticationLogin, UserUpdateFrom, PasswordResetRequestForm, SetPassword
from PROFILE.models import User
from PROFILE.forgetpasswordtoken import reset_password_token



class Login(LoginView):
    form_class = UserAuthenticationLogin
    template_name = 'Profile/login.html'
    success_url = reverse_lazy('index')
    redirect_authenticated_user = True


class RegisterView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'Profile/registration.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("index")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.otp_attempts = 3
        user.reset_timer = None
        user.save()

        device, _ = EmailDevice.objects.get_or_create(user=user, name='default', email=user.email)
        device.generate_challenge()
        user.last_otp_sent = timezone.now()
        user.save()

        return redirect('verify_otp', pk=user.id)


def get_otp_context(user):
    otp_validity_seconds = getattr(settings, "OTP_EMAIL_TOKEN_VALIDITY", 300)
    max_attempts = getattr(settings, "OTP_LOGIN_ATTEMPT", 3)
    email_reset_time = getattr(settings, "EMAIL_RESET_TIME", 30)

    last_otp_sent = getattr(user, "last_otp_sent", None)
    otp_expires_at = last_otp_sent + timedelta(seconds=otp_validity_seconds) if last_otp_sent else None

    return {
        "user": user,
        "last_otp_sent": last_otp_sent,
        "otp_expires_at": otp_expires_at,
        "otp_validity_minutes": otp_validity_seconds // 60,
        "attempts_left": user.otp_attempts,
        "max_attempts": max_attempts,
        "email_reset_time": email_reset_time,
    }


class VerifyOTPView(View):
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)

        if user.is_active:
            return redirect("login")

        # If locked
        if user.reset_timer and user.reset_timer > timezone.now():
            messages.error(request, "Account locked. Try again later.")
            return redirect("create_user")

        return render(request, "Profile/verify_otp.html", get_otp_context(user))

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        otp_code = request.POST.get("otp")

        # Lockout check
        if user.reset_timer and user.reset_timer > timezone.now():
            messages.error(request, "Account is locked. Try again later.")
            return redirect("create_user")

        device = EmailDevice.objects.filter(user=user, name="default").first()
        if not device:
            messages.error(request, "No OTP device found. Please register again.")
            return redirect("create_user")

        # Expiry check
        otp_validity_seconds = getattr(settings, "OTP_EMAIL_TOKEN_VALIDITY", 300)
        otp_expired = (
            not user.last_otp_sent or
            timezone.now() > user.last_otp_sent + timedelta(seconds=otp_validity_seconds)
        )

        if otp_expired:
            # Don't even check against device → already invalid
            messages.error(request, "OTP has expired. Please request a new one.")
            return render(request, "Profile/verify_otp.html", {**get_otp_context(user), "otp_expired": True})
        
        # Verification
        if device.verify_token(otp_code):
            user.is_active = True
            user.otp_attempts = 3
            user.reset_timer = None
            user.save()
            messages.success(request, "Account verified! Please login.")
            return redirect("login")
        else:
           if not user.is_active:  # Only apply OTP checks if user is not verified
            user.otp_attempts -= 1
            if user.otp_attempts <= 0:
                user.reset_timer = timezone.now() + timedelta(minutes=30)
                user.save()
                messages.error(request, "Too many attempts. Account locked for 30 minutes.")
                return redirect("create_user")

            user.save()
            messages.error(request, f"Invalid OTP. Attempts left: {user.otp_attempts}")
            return render(request, "Profile/verify_otp.html", get_otp_context(user))

        # If already active → don’t process OTP attempts
        messages.info(request, "Your account is already verified. Please login.")
        return redirect("login")


# this view is for after 30 minutes lockout 
# user is register but not verified
# here we resend otp and reset attempts if lockout period expired
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
        if (
            not device.confirmed
            or device.last_generated_timestamp is None
            or timezone.now() > device.last_generated_timestamp + timedelta(minutes=2)
        ):            
            device.generate_challenge()  # send OTP
            device.save()

            # FIX: update user last_otp_sent for expiry tracking
            user.last_otp_sent = timezone.now()
            user.save(update_fields=["last_otp_sent"])

            messages.info(request, "We have sent you a new OTP.")

        return render(request, "Profile/verify_otp.html", get_otp_context(user))


class AccountProfile(UpdateView):
    model = User
    form_class = UserUpdateFrom
    template_name = 'Profile/profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user
  

def password_reset_request(request):
    login_form = UserAuthenticationLogin()
    reset_form = PasswordResetRequestForm(request.POST or None)

    if request.method == "POST" and reset_form.is_valid():
        email = reset_form.cleaned_data['email']
        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            messages.success(request, "Password reset link sent to your email.")
            return redirect('login')

        # Check cooldown: 3 minutes
        if user.last_password_link_sent and timezone.now() < user.last_password_link_sent + timedelta(minutes=3):
            remaining = (user.last_password_link_sent + timedelta(minutes=30) - timezone.now()).seconds
            messages.error(
                request, 
                f"Please wait {remaining // 60} minutes and {remaining % 60} seconds before requesting another link."
            )
            return render(request, "Profile/login.html", {'form': login_form, 'password_reset_form': reset_form})

        # Generate token and send email
        token = reset_password_token.make_token(user)
        reset_url = request.build_absolute_uri(
            reverse('password_reset_confirm', kwargs={'email': quote(user.email), 'token': token})
        )
        send_mail(
            "🔐 Password Reset Request from Unify Store",
            f"Click the link to reset your password (valid for 30 minutes): {reset_url}",
            "shivangikeshri21@gmail.com",
            [user.email],
            fail_silently=False
        )

        user.reset_timer = timezone.now()  # track 30-min expiry for token
        user.last_password_link_sent = timezone.now()  # track 3-min cooldown
        user.save()

        messages.success(request, "Password reset link sent to your email.")

    return render(request, "Profile/login.html", {'form': login_form, 'password_reset_form': reset_form})


def password_reset_confirm(request, email, token):
    email = email.replace('%40', '@') 
    user = get_object_or_404(User, email=email, is_active=True)

    # Token and 30-min expiration check
    if not reset_password_token.check_token(user, token):
        messages.error(request, "The password reset link is invalid")
        form = SetPassword(user)  # unbound form
        return render(request, "Profile/reset_password.html", {'form': form})

    if user.reset_timer and timezone.now() > user.reset_timer + timedelta(minutes=30):
        messages.error(request, "The password reset link has expired.")
        form = SetPassword(user)
        return render(request, "Profile/reset_password.html", {'form': form})

    if request.method == "POST":
        form = SetPassword(user, request.POST)
        if form.is_valid():
            form.save()
            user.reset_timer = None
            user.save()
            messages.success(request, "Your password has been reset successfully.")
            return redirect('login')
    else:
        form = SetPassword(user) 

    return render(request, "Profile/reset_password.html", {'form': form})


# Add Address View
