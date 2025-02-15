from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import datetime


class UserPOI(models.Model):
    """
    User-Defined Points of Interest
    """

    name = models.CharField(max_length=100, primary_key=True)
    latitude = models.FloatField(
        null=False, validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)]
    )
    longitude = models.FloatField(
        null=False, validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)]
    )
    location = models.PointField(null=True)
    address = models.CharField(blank=True, max_length=255)
    city = models.CharField(blank=True, max_length=50)
    country = models.CharField(blank=True, max_length=50)
    updated_at = models.DateTimeField("Updated at", auto_now=True)

    def __str__(self):
        return self.name

    def update_location(self):
        try:
            if self.latitude is not None and self.longitude is not None:
                self.location = Point(float(self.longitude), float(self.latitude))
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Invalid latitude or longitude values: {e}")

    def save(self, *args, **kwargs):
        self.update_location()
        self.full_clean()
        super().save(*args, **kwargs)


class Tile(models.Model):
    """
    Tile uuid to name mapping
    """
    uuid = models.CharField(max_length=36, primary_key=True)  # not in proper uuid format
    name = models.CharField(null=False, blank=False, max_length=100, unique=True)
    updated_at = models.DateTimeField("Updated at", auto_now=True)
    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class TileSegment(models.Model):
    """
    Tile location segments
    """

    uuid = models.CharField(null=False, max_length=36)
    name = models.CharField(null=False, max_length=100)

    latitude = models.FloatField(
        null=False, validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)]
    )
    longitude = models.FloatField(
        null=False, validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)]
    )
    segment = models.SmallIntegerField(null=False)
    state = models.CharField(max_length=20)
    start_segment = models.DateTimeField()
    last_timestamp_utc = models.DateTimeField(null=False)
    retrieved_at_utc = models.DateTimeField(null=False)
    updated_at = models.DateTimeField("Updated at", auto_now=True)

    class Meta:
        unique_together = ("uuid", "last_timestamp_utc")
        indexes = [
            models.Index(fields=["name"], name="idx_name"),
            models.Index(fields=["start_segment"], name="idx_start_segment"),
            models.Index(fields=["last_timestamp_utc"], name="idx_last_timestamp_utc"),
        ]
        ordering = ["start_segment"]

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
