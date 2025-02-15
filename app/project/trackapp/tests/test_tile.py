from trackapp.models import Tile
from django.test import TestCase
from django.core.exceptions import ValidationError


class TileModelTests(TestCase):
    def test_name_unique(self):
        Tile(uuid='testtile1', name='mytile').save()
        with self.assertRaises(ValidationError):
            Tile(uuid='testtile2', name='mytile').save()
    
    def test_name_not_null_or_blank(self):
        with self.assertRaises(ValidationError):
            Tile(uuid='testtile3').save()
            Tile(uuid='testtile4', name='').save()
