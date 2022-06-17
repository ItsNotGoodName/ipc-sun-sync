from datetime import datetime

from astral.sun import sun


def get_sunrise_and_sunset(config):
    times = sun(
        config["location"].observer,
        date=datetime.now(config["timezone"]),
        tzinfo=config["timezone"],
    )
    return (times["sunrise"], times["sunset"])


def valid_sunrise_and_sunset(sunrise, sunset):
    sunrise_midnight = sunrise.replace(hour=0, minute=0, second=0, microsecond=0)
    sunrise_seconds = (sunrise - sunrise_midnight).seconds
    sunset_midnight = sunset.replace(hour=0, minute=0, second=0, microsecond=0)
    sunset_seconds = (sunset - sunset_midnight).seconds
    return sunrise_seconds < sunset_seconds
