import logging
import traceback

import pytz

from . import __version__
from .constants import IPC, ConfigIPC, ConfigMethod
from .dahua_cgi import DahuaCgi
from .dahua_rpc import DahuaRpc
from .parser import parse_args, parse_yml_or_exit, parse_config_or_exit
from .utils import get_sunrise_and_sunset, valid_dahua_sunrise_and_sunset


def main():
    args = parse_args()

    # Print version
    if args.version:
        print(__version__)
        return

    # Print timezones
    if args.timezones:
        for t in pytz.all_timezones:
            print(t)
        return

    config = parse_config_or_exit(parse_yml_or_exit(args.path))
    ret_code = 0

    # Check all ipc
    if args.check:
        for c in config["ipc"]:
            try:
                ipc = get_ipc(c)
                sunrise, sunset, switch_mode = ipc.get_sunrise_and_sunset(c["channel"])
            except Exception as e:
                print(traceback.format_exc())
                logging.error(e)
                ret_code = 1
                continue
            print(
                f"{c['name']} sunrise is {sunrise}, sunset is {sunset}, and switch mode is set to {switch_mode}"
            )
        return ret_code

    # Sync all ipc
    sunrise, sunset = get_sunrise_and_sunset(config["location"])
    print(
        "sunrise is %s and sunset is %s for %s"
        % (
            sunrise.strftime("%X"),
            sunset.strftime("%X"),
            sunrise.strftime("%x"),
        )
    )
    if not valid_dahua_sunrise_and_sunset(sunrise, sunset):
        logging.error(
            "daytime hours are not within a single day (e.g. sunrise 1:00 PM and sunset 12:01 AM the next day), check if your timezone and coordinates are correct"
        )
        return 1

    for c in config["ipc"]:
        print("syncing %s on channel %s..." % (c["name"], c["channel"]))

        try:
            get_ipc(c).set_sunrise_and_sunset(
                sunrise=sunrise,
                sunset=sunset,
                channel=c["channel"],
            )
        except Exception as e:
            print(traceback.format_exc())
            logging.error(e)
            ret_code = 1
            continue

        print("synced %s on channel %s" % (c["name"], c["channel"]))

    return ret_code


def get_ipc(ipc_config: ConfigIPC) -> IPC:
    if ipc_config["method"] == ConfigMethod.CGI:
        return DahuaCgi(
            ip=ipc_config["ip"],
            username=ipc_config["username"],
            password=ipc_config["password"],
        )
    if ipc_config["method"] == ConfigMethod.RPC:
        rpc = DahuaRpc(
            ip=ipc_config["ip"],
            username=ipc_config["username"],
            password=ipc_config["password"],
        )
        rpc.login()
        return rpc

    raise Exception("unknown method %s" % ipc_config["method"])
