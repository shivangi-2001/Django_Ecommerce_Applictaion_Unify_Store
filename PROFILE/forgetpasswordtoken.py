from django.contrib.auth.tokens import PasswordResetTokenGenerator

class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        # Including last_otp_sent or last_login to invalidate old tokens
        return f"{user.pk}{user.password}{timestamp}"

reset_password_token = TokenGenerator()
