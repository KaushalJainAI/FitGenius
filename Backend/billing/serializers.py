from rest_framework import serializers

from .models import Subscription


class SubscriptionSerializer(serializers.ModelSerializer):
    plan_label = serializers.ReadOnlyField()
    is_trial_active = serializers.ReadOnlyField()
    price = serializers.SerializerMethodField()
    billing_cycle = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = [
            'id', 'plan', 'plan_label', 'status', 'price', 'billing_cycle',
            'trial_started_at', 'trial_ends_at', 'is_trial_active',
            'cancel_at_period_end', 'current_period_start', 'current_period_end',
            'manual_validation_note', 'features', 'created_at', 'updated_at',
        ]
        read_only_fields = fields

    def get_price(self, obj):
        return 0

    def get_billing_cycle(self, obj):
        return 'free_trial' if obj.status == Subscription.STATUS_TRIALING else 'free'

    def get_features(self, obj):
        if obj.plan == Subscription.PLAN_PRO:
            return [
                'AI workout and diet recommendations',
                'Daily readiness based plan updates',
                'Progress analytics',
                'Priority Pro trial access',
            ]

        return [
            'Basic profile and check-ins',
            'Starter recommendations',
            'Limited progress tracking',
        ]


class ManualPlanActionSerializer(serializers.Serializer):
    note = serializers.CharField(required=False, allow_blank=True, max_length=500)

