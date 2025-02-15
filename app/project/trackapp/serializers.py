from .models import UserPOI, TileSegment
from rest_framework import serializers


class V1UserPOISerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPOI
        fields = [
            "name",
            "latitude",
            "longitude",
            "address",
            "city",
            "country",
            "updated_at",
        ]


class V1TileSegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TileSegment
        fields = [
            "name",
            "latitude",
            "longitude",
            "state",
            "start_segment",
            "last_timestamp_utc",
        ]
