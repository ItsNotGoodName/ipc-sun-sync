import logging

from yaml import YAMLError
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
            "Sunrise and sunset interval is not within a single day. Check if your timezone and coordinates are correct."
        )
        return 1

    if args.daemon:
        logging.error("Daemon not implemented")
        return 1
    else:
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
