from django.shortcuts import render
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from .filters import UserPOIFilter, TileSegmentFilter
from .models import UserPOI, TileSegment
from .serializers import V1UserPOISerializer, V1TileSegmentSerializer
from .utils import get_most_recent_location, clean_segments
from datetime import datetime, timezone


# V1 API views
class UserPOIAPIView(generics.ListAPIView):
    queryset = UserPOI.objects.all().order_by("name")
    serializer_class = V1UserPOISerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserPOIFilter


class TileSegmentAPIView(generics.ListAPIView):
    queryset = TileSegment.objects.all().order_by("-last_timestamp_utc")
    serializer_class = V1TileSegmentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TileSegmentFilter


# Map views
def places(request):

    # Get the name filter from the request, if present
    # TO DO: Validate name_filter
    name_filter = request.GET.get("name", "")

    userloc = get_most_recent_location(name_filter)
    if not userloc:
        userloc = get_most_recent_location("", is_demo=True)

    places = UserPOI.objects.all()

    points = [
        {
            "name": plc.name,
            "latitude": plc.latitude,
            "longitude": plc.longitude,
            "address": plc.address,
        }
        for plc in places
    ]

    return render(request, "poimap.html", {"user_location": userloc, "points": points})


def tracks(request):

    name_filter = request.GET.get("name", "")
    from_time_filter = request.GET.get("from_time", "2025-01-17")
    to_time_filter = request.GET.get("to_time", "2025-02-11")

    # Tracks
    tracks = (
        TileSegment.objects.filter(
            name=name_filter,
            last_timestamp_utc__gte=from_time_filter,
            last_timestamp_utc__lte=to_time_filter,
        )
        .order_by("last_timestamp_utc")
        .only(
            "name",
            "state",
            "latitude",
            "longitude",
            "start_segment",
            "last_timestamp_utc",
        )
    )
    cleaned_tracks = clean_segments(
        tracks,
        datetime.strptime(from_time_filter, "%Y-%m-%d").replace(tzinfo=timezone.utc),
    )

    # Superimpose with places of interest
    places = UserPOI.objects.all()
    pois = [
        {
            "name": plc.name,
            "latitude": plc.latitude,
            "longitude": plc.longitude,
            "address": plc.address,
        }
        for plc in places
    ]

    return render(
        request, "trackmap.html", {"track_data": cleaned_tracks, "pois": pois}
    )
