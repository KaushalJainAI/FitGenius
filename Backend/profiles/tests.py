from datetime import date

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from .models import DailyCheckIn


class DailyCheckInEndpointTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="checkin-user",
            email="checkin-user@example.com",
            password="pass12345",
        )

    def test_latest_uses_newest_date_then_created_at_ordering(self):
        older = DailyCheckIn.objects.create(
            user=self.user,
            date=date(2026, 5, 1),
            energy_level=1,
        )
        newer = DailyCheckIn.objects.create(
            user=self.user,
            date=date(2026, 5, 2),
            energy_level=5,
        )
        self.client.force_authenticate(self.user)

        response = self.client.get("/api/checkins/latest/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], newer.id)
        self.assertNotEqual(response.data["id"], older.id)
