from django.test import TestCase, Client
from django.urls import reverse
from trackapp.models import UserPOI
from trackapp.serializers import V1UserPOISerializer, V1TileSegmentSerializer


class V1APITests(TestCase):
    def setUp(self):
        self.client = Client()  # Django test client

    def test_places_api(self):
        # Based on UserPOI
        response = self.client.get(reverse('trackapp:poi-api'))
        self.assertEqual(response.status_code, 200)  # Check response status

        # Some records are already available through migration steps
        data = response.json()
        self.assertTrue(data.get('count') > 1)

        # json keys
        self.assertEqual(
            set(data.get('results')[0].keys()),
            set(V1UserPOISerializer().fields.keys())
        )

    def test_tracks_api(self):
        # TO DO
        # To mock tracks data
        pass
