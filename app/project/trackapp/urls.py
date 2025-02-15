from django.urls import path
from . import views


app_name = "trackapp"

urlpatterns = [
    path("map/places", views.places, name="poi-map"),
    path("map/tracks", views.tracks, name="track-map"),
    path("api/v1/places", views.UserPOIAPIView.as_view(), name="poi-api"),
    path("api/v1/tracks", views.TileSegmentAPIView.as_view(), name="tracks-api"),
]
