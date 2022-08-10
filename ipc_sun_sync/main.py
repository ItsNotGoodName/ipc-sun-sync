import logging
import traceback

import pytz

from . import __version__
from .constants import IPC, ConfigIPC, ConfigMethod
from .dahua_cgi import DahuaCgi
from .dahua_rpc import DahuaRpc
from .parser import parse_args, parse_yml_or_exit, parse_config_or_exit
from .utils import sunrise_and_sunset_from_location, valid_dahua_sunrise_and_sunset


def main():
    ret_code = 0

    #################### Print arguments ####################
    args = parse_args()

    #################### Print version ####################
    if args.version:
        print(__version__)
        return ret_code

    ####################  Print timezones ####################
    if args.timezones:
        for t in pytz.all_timezones:
            print(t)
        return ret_code

    config = parse_config_or_exit(parse_yml_or_exit(args.path))

    #################### Verify ipc settings ####################
    if args.verify:
        for c in config["ipc"]:
            try:
                sunrise, sunset, switch_mode = get_ipc(c).get_sunrise_and_sunset(
                    c["channel"]
                )
            except Exception as e:
                print(traceback.format_exc())
                logging.error("%s: %s", e, c["name"])
                ret_code = 1
                continue
            print(
                f"{c['name']} sunrise is {sunrise}, sunset is {sunset}, and switch mode is set to {switch_mode}"
            )
        return ret_code

    #################### Check configuration ####################
    sunrise, sunset = sunrise_and_sunset_from_location(config["location"])

    if args.check:
        print(f"timezone: {config['location'].timezone}")
        print(f"lattitude: {config['location'].latitude}")
        print(f"longitude: {config['location'].longitude}")
        print(f"sunrise: {sunrise.strftime('%X')}")
        print(f"sunset: {sunset.strftime('%X')}")
        print("ipc:")
        for c in config["ipc"]:
            print(f"  - name: {c['name']}")
            print(f"    ip: {c['ip']}")
            print(f"    channel: {c['channel']}")
            print(f"    username: {c['username']}")
            print(f"    method: {c['method']}")
            print(f"    sunrise: {(sunrise+c['sunrise_offset']).strftime('%X')}")
            print(f"    sunset: {(sunset+c['sunset_offset']).strftime('%X')}")
        return ret_code

    #################### Sync ####################
    print(
        f"sunrise is {sunrise.strftime('%X')} and sunset is {sunset.strftime('%X')} for {sunrise.strftime('%x')}"
    )

    for c in config["ipc"]:
        print(f"syncing {c['name']} on channel {c['channel']}...")

        new_sunrise = sunrise + c["sunrise_offset"]
        new_sunset = sunset + c["sunset_offset"]
        if not valid_dahua_sunrise_and_sunset(new_sunrise, new_sunset):
            logging.error(
                "daytime hours are not within a single day, check if your timezone, sun offsets, and coordinates are correct: sunrise is %s and sunset is %s",
                new_sunrise.strftime("%X"),
                new_sunset.strftime("%X"),
            )
            ret_code = 1
            continue

        try:
            get_ipc(c).set_sunrise_and_sunset(
                sunrise=new_sunrise,
                sunset=new_sunset,
                channel=c["channel"],
            )
        except Exception as e:
            print(traceback.format_exc())
            logging.error("%s: %s", e, c["name"])
            ret_code = 1
            continue

        print(f"synced {c['name']} on channel {c['channel']}")

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

    raise Exception(f"unknown method '{ipc_config['method']}'")
