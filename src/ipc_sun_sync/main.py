import logging

import pytz

from . import ipc, __version__
from .parser import parse_args, parse_yml, parse_config
from .utils import get_sunrise_and_sunset, valid_sunrise_and_sunset


def main():
    args = parse_args()
    if args.version:
        print(__version__)
        return
    if args.timezones:
        for t in pytz.all_timezones:
            print(t)
        return

    yml = parse_yml(args.path)
    if not yml:
        return 1

    config = parse_config(yml)
    sunrise, sunset = get_sunrise_and_sunset(config)
    print(
        "Sunrise is at %s and sunset is at %s for %s"
        % (
            sunrise.strftime("%X"),
            sunset.strftime("%X"),
            sunrise.strftime("%x"),
        )
    )
    if not valid_sunrise_and_sunset(sunrise, sunset):
        logging.error(
            "Daytime hours are not within a single day (e.g. sunrise 1:00 PM and sunset 12:01 AM the next day), check if your timezone and coordinates are correct"
        )
        return 1

    for c in config["ipc"]:
        if ipc.sync(
            ip=c["ip"],
            username=c["username"],
            password=c["password"],
            sunrise=sunrise,
            sunset=sunset,
            channel=c["channel"],
        ):
            print(
                "Sunrise and sunset synced for %s on channel %s"
                % (c["name"], c["channel"])
            )
        else:
            print("Unable to sync sunrise and sunset for %s" % c["name"])
