from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Subscription
from .serializers import ManualPlanActionSerializer, SubscriptionSerializer


class SubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        subscription = Subscription.get_or_create_for_user(request.user)
        return Response(SubscriptionSerializer(subscription).data)


class BillingPlansView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'plans': [
                {
                    'id': Subscription.PLAN_FREE,
                    'label': 'Free',
                    'price': 0,
                    'billing_cycle': 'free',
                    'features': [
                        'Basic profile',
                        'Daily check-ins',
                        'Starter recommendations',
                    ],
                },
                {
                    'id': Subscription.PLAN_PRO,
                    'label': 'Pro Trial',
                    'price': 0,
                    'billing_cycle': 'free_trial',
                    'trial_days': 14,
                    'features': [
                        'Adaptive AI plans',
                        'Progress analytics',
                        'Manual free-trial validation',
                    ],
                },
            ],
        })


class StartProTrialView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ManualPlanActionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'detail': 'Invalid trial upgrade request.', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription = Subscription.get_or_create_for_user(request.user)
        note = serializer.validated_data.get('note') or 'Manual free trial upgrade'
        subscription.start_pro_trial(note=note)
        return Response({
            'success': True,
            'message': 'Pro free trial started.',
            'data': SubscriptionSerializer(subscription).data,
        }, status=status.HTTP_200_OK)


class CancelSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ManualPlanActionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'detail': 'Invalid cancellation request.', 'errors': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription = Subscription.get_or_create_for_user(request.user)
        note = serializer.validated_data.get('note') or 'Manual cancellation to free plan'
        subscription.cancel_to_free(note=note)
        return Response({
            'success': True,
            'message': 'Subscription moved to Free.',
            'data': SubscriptionSerializer(subscription).data,
        }, status=status.HTTP_200_OK)
