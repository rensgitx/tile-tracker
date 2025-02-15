import django_filters
from .models import UserPOI, TileSegment


class UserPOIFilter(django_filters.FilterSet):
    class Meta:
        model = UserPOI
        fields = {"name": ["exact", "icontains"]}


class TileSegmentFilter(django_filters.FilterSet):
    class Meta:
        model = TileSegment
        fields = {
            "name": ["exact", "icontains"],
            "start_segment": ["lt", "gt", "lte", "gte"],
            "last_timestamp_utc": ["lt", "gt", "lte", "gte"],
        }
