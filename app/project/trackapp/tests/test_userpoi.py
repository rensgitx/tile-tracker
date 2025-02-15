from trackapp.models import UserPOI
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.gis.geos import Point


class UserPOIModelTests(TestCase):

    def test_latlon_is_within_range(self):
        # out-of-range
        oor_lls = [(200.0, 200.0), (100.1, 72.01), (43.2, -190.51)]
        for (ix, ll) in enumerate(oor_lls):
            with self.assertRaises(ValidationError):
                UserPOI(name=f'testpoi{ix}', latitude=ll[0], longitude=ll[1]).save()
        # within range
        ll = UserPOI.objects.create(name='testpoivalidlatlon', latitude=43.0, longitude=72.5)
        self.assertTrue(UserPOI.objects.filter(name='testpoivalidlatlon').exists()) 

    def test_location_exists(self):
        ll = UserPOI.objects.create(name='testpoilocation', latitude=42.51, longitude=72.522)
        self.assertIsInstance(ll.location, Point)

    def test_name_unique(self):
        UserPOI(name='testpoiname', latitude=42.51, longitude=72.522).save()
        with self.assertRaises(ValidationError):
            UserPOI(name='testpoiname', latitude=42.511, longitude=72.5221).save()
