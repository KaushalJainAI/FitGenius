from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class Subscription(models.Model):
    PLAN_FREE = 'free'
    PLAN_PRO = 'pro'
    PLAN_CHOICES = [
        (PLAN_FREE, 'Free'),
        (PLAN_PRO, 'Pro'),
    ]

    STATUS_ACTIVE = 'active'
    STATUS_TRIALING = 'trialing'
    STATUS_CANCELED = 'canceled'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_TRIALING, 'Trialing'),
        (STATUS_CANCELED, 'Canceled'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscription',
    )
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default=PLAN_FREE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    trial_started_at = models.DateTimeField(null=True, blank=True)
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    manual_validation_note = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    @classmethod
    def get_or_create_for_user(cls, user):
        now = timezone.now()
        subscription, _ = cls.objects.get_or_create(
            user=user,
            defaults={
                'plan': cls.PLAN_FREE,
                'status': cls.STATUS_ACTIVE,
                'current_period_start': now,
                'current_period_end': now + timedelta(days=30),
            },
        )
        return subscription

    def start_pro_trial(self, days=14, note='Manual free trial upgrade'):
        now = timezone.now()
        self.plan = self.PLAN_PRO
        self.status = self.STATUS_TRIALING
        self.trial_started_at = now
        self.trial_ends_at = now + timedelta(days=days)
        self.current_period_start = now
        self.current_period_end = self.trial_ends_at
        self.cancel_at_period_end = False
        self.manual_validation_note = note
        self.save()

    def cancel_to_free(self, note='Manual cancellation to free plan'):
        now = timezone.now()
        self.plan = self.PLAN_FREE
        self.status = self.STATUS_ACTIVE
        self.cancel_at_period_end = False
        self.current_period_start = now
        self.current_period_end = now + timedelta(days=30)
        self.manual_validation_note = note
        self.save()

    @property
    def is_trial_active(self):
        return self.status == self.STATUS_TRIALING and self.trial_ends_at and self.trial_ends_at > timezone.now()

    @property
    def plan_label(self):
        return dict(self.PLAN_CHOICES).get(self.plan, self.plan.title())
