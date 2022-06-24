import logging
import traceback

import pytz

from . import __version__
from .dahua_cgi import DahuaCgi
from .parser import parse_args, parse_yml_or_exit, parse_config_or_exit
from .utils import get_sunrise_and_sunset, valid_dahua_sunrise_and_sunset


def main():
    args = parse_args()
    if args.version:
        print(__version__)
        return
    if args.timezones:
        for t in pytz.all_timezones:
            print(t)
        return

    config = parse_config_or_exit(parse_yml_or_exit(args.path))
    sunrise, sunset = get_sunrise_and_sunset(config["location"])
    print(
        "Sunrise is at %s and sunset is at %s for %s"
        % (
            sunrise.strftime("%X"),
            sunset.strftime("%X"),
            sunrise.strftime("%x"),
        )
    )
    if not valid_dahua_sunrise_and_sunset(sunrise, sunset):
        logging.error(
            "Daytime hours are not within a single day (e.g. sunrise 1:00 PM and sunset 12:01 AM the next day), check if your timezone and coordinates are correct"
        )
        return 1

    code = 0

    for c in config["ipc"]:
        print("Syncing %s on channel %s..." % (c["name"], c["channel"]))

        if c["method"] == "cgi":
            try:
                DahuaCgi(c["ip"], c["username"], c["password"]).set_sunrise_and_sunset(
                    sunrise=sunrise,
                    sunset=sunset,
                    channel=c["channel"],
                )
            except Exception as e:
                print(traceback.format_exc())
                logging.error("Unable to sync %s", c["name"], e)
                code = 1
                continue
        elif c["method"] == "rpc":
            logging.error("rpc is not implemented")
            continue
        else:
            logging.error("Invalid method %s", c["method"])
            continue

        print("Synced %s on channel %s" % (c["name"], c["channel"]))

    return code
