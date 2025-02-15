from django.contrib.gis.admin import GISModelAdmin
from django.contrib.admin import ModelAdmin
from django.contrib import admin
from .models import Tile, UserPOI, TileSegment


@admin.register(Tile)
class TileAdmin(ModelAdmin):
    list_display = (
        "uuid",
        "name",
        "updated_at",
    )

@admin.register(UserPOI)
class UserPOIAdmin(GISModelAdmin):
    list_display = ("name", "latitude", "longitude", "address", "city", "country")


@admin.register(TileSegment)
class TileSegmentAdmin(ModelAdmin):
    list_display = (
        "name",
        "latitude",
        "longitude",
        "segment",
        "state",
        "start_segment",
        "last_timestamp_utc",
        "updated_at",
    )
