from django.urls import path, include

from PROFILE.views import RegisterView, VerifyOTPView, Login

urlpatterns = [
    path('auth/register', RegisterView.as_view(), name="create_user"),
    path('auth/<int:pk>/verify_otp', VerifyOTPView.as_view(), name='verify_otp'),
    path('login', Login.as_view(), name='login')
]