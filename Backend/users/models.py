from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model for FitGenius AI.
    Email-based authentication (like NGU).
    """
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return self.email


class PasswordResetOTP(models.Model):
    """
    Model to store OTPs for password reset requests.
    """
    MAX_FAILED_ATTEMPTS = 5

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_otps')
    otp_code = models.CharField(max_length=255)
    reset_token = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    failed_attempts = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - OTP Request"

    def set_otp(self, raw_otp):
        from django.contrib.auth.hashers import make_password
        self.otp_code = make_password(raw_otp)

    def check_otp(self, raw_otp):
        from django.contrib.auth.hashers import check_password
        # Support fallback to plaintext if old record
        if len(self.otp_code) == 6 or '$' not in self.otp_code:
            return self.otp_code == raw_otp
        return check_password(raw_otp, self.otp_code)

    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at

    @property
    def is_locked(self):
        """OTP is locked after too many failed verification attempts."""
        return self.failed_attempts >= self.MAX_FAILED_ATTEMPTS


class UserPreference(models.Model):
    """User-owned app preferences that were previously localStorage-only."""

    THEME_CHOICES = [
        ('light', 'Light'),
        ('dark', 'Dark'),
    ]
    MEASUREMENT_CHOICES = [
        ('metric', 'Metric'),
        ('imperial', 'Imperial'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')
    measurement_system = models.CharField(max_length=10, choices=MEASUREMENT_CHOICES, default='metric')
    push_enabled = models.BooleanField(default=False)
    reminder_time = models.TimeField(default='08:00')
    weekly_email_enabled = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Preference'
        verbose_name_plural = 'User Preferences'

    def __str__(self):
        return f"{self.user.email} preferences"

    @classmethod
    def get_or_create_for_user(cls, user):
        preferences, _ = cls.objects.get_or_create(user=user)
        return preferences
