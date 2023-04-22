"""sunrise_sunset tap class."""

from typing import List

from singer_sdk import Tap, Stream
from singer_sdk import typing as th  # JSON schema typing helpers
# TODO: Import your custom stream types here:
from tap_sunrise_sunset.streams import (
    sunrise_sunsetStream,
    dataStream
)
# TODO: Compile a list of custom stream types here
#       OR rewrite discover_streams() below with your custom logic.
STREAM_TYPES = [
    dataStream
]


class Tapsunrise_sunset(Tap):
    """sunrise_sunset tap class."""
    name = "tap-sunrise-sunset"

    # TODO: Update this section with the actual config values you expect:
    config_jsonschema = th.PropertiesList(
        th.Property(
            "lat",
            th.StringType,
            required=True,
            description="Latitude of the place"
        ),
        th.Property(
            "lng",
            th.StringType,
            required=True,
            description="Longitude of the place"
        ),
        th.Property(
            "start_date",
            th.DateType,
            required=True,
            description="The earliest record date to sync"
        ),
        th.Property(
            "end_date",
            th.DateType,
            required=True,
            description="End date for sync"
        ),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]
