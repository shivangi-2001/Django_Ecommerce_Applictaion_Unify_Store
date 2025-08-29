from django.urls import path, include
from django.contrib.auth.views import LogoutView
from PROFILE.views import RegisterView, VerifyOTPView, Login, AccountProfile, VerifyAccount, password_reset_request, password_reset_confirm

urlpatterns = [
    path('auth/register', RegisterView.as_view(), name="create_user"),
    path('auth/<int:pk>/verify_otp', VerifyOTPView.as_view(), name='verify_otp'),

    path('login', Login.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('account/verify', VerifyAccount.as_view(), name='verify_account'),

    path('auth/<str:pk>/accounts/profile', AccountProfile.as_view(), name='profile'),

    path('password-reset/', password_reset_request, name='password_reset_request'),
    path('password-reset-confirm/<str:email>/<str:token>/', password_reset_confirm, name='password_reset_confirm')

]