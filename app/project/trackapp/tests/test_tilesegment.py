from trackapp.models import TileSegment
from django.test import TestCase
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta, timezone
from typing import Any, Dict
import random, string, time


random.seed(time.time())

class TileSegmentModelTests(TestCase):

    @classmethod
    def create_test_data(cls, **kwargs) -> Dict[str, Any]:
        default = {
            'uuid': ''.join(random.choices(string.digits, k=8)),
            'name': ''.join(random.choices(string.ascii_letters, k=8)),
            'latitude': -43.51,
            'longitude': 72.110,
            'segment': 1,
            'state': 'default_state',
            'start_segment': datetime.now(timezone.utc) - timedelta(hours=-3),
            'last_timestamp_utc': datetime.now(timezone.utc),
            'retrieved_at_utc': datetime.now(timezone.utc),
        }
        for label, val in kwargs.items():
            default[label] = val
        return default

    def test_uuid_not_null_or_blank(self):
        with self.assertRaises(ValidationError):
            TileSegment(**self.create_test_data(uuid=None)).save()

        with self.assertRaises(ValidationError):
            TileSegment(**self.create_test_data(uuid='')).save()

    def test_latlon_is_within_range(self):
        # out-of-range
        oor_lls = [(200.0, 200.0), (100.1, 72.01), (43.2, -190.51)]
        for lat, lon in oor_lls:
            with self.assertRaises(ValidationError):
                TileSegment(**self.create_test_data(latitude=lat, longitude=lon)).save()
        # within range
        testdata = self.create_test_data(latitude=-40, longitude=82.0)
        segment = TileSegment.objects.create(**testdata)
        self.assertTrue(TileSegment.objects.filter(name=segment.name).exists())
