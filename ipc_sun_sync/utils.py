from datetime import datetime

import astral
import astral.sun


def get_sunrise_and_sunset(location: astral.LocationInfo):
    times = astral.sun.sun(
        location.observer,
        tzinfo=location.tzinfo,
    )
    return (times["sunrise"], times["sunset"])


def valid_dahua_sunrise_and_sunset(sunrise: datetime, sunset: datetime):
    sunrise_midnight = sunrise.replace(hour=0, minute=0, second=0, microsecond=0)
    sunrise_seconds = (sunrise - sunrise_midnight).seconds
    sunset_midnight = sunset.replace(hour=0, minute=0, second=0, microsecond=0)
    sunset_seconds = (sunset - sunset_midnight).seconds
    return sunrise_seconds < sunset_seconds