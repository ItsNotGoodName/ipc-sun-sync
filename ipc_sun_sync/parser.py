import argparse
import pathlib
import sys
import logging
from typing import Dict

import astral
import pytz
import yaml

from .constants import Config, ConfigMethod, ConfigIPC
from . import __description__


def parse_args():
    parser = argparse.ArgumentParser(description=__description__)
    parser.add_argument(
        "--check", action="store_true", dest="check", help="check all ipc"
    )
    parser.add_argument(
        "-c",
        "--config",
        type=pathlib.Path,
        metavar="PATH",
        dest="path",
        required="-V" not in sys.argv
        and "--version" not in sys.argv
        and "-T" not in sys.argv
        and "--timezones" not in sys.argv,
        help="configuration file path",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        action="store_true",
        help="enable verbose logging",
    )
    parser.add_argument(
        "-V",
        "--version",
        dest="version",
        action="store_true",
        help="show version",
    )
    parser.add_argument(
        "-T",
        "--timezones",
        dest="timezones",
        action="store_true",
        help="show all timezones",
    )
    return parser.parse_args()


def parse_yml_or_exit(path: pathlib.Path):
    try:
        with path.open(mode="r") as stream:
            return yaml.safe_load(stream)
    except FileNotFoundError:
        logging.error("File '%s' does not exist", path)
    except PermissionError:
        logging.error("File '%s' is not readable", path)
    except yaml.YAMLError as error:
        logging.error(error)
    exit(1)


def parse_method_or_exit(yml: Dict) -> ConfigMethod:
    if "method" not in yml:
        return ConfigMethod.CGI
    if yml["method"] == "cgi":
        return ConfigMethod.CGI
    if yml["method"] == "rpc":
        return ConfigMethod.RPC

    logging.error("method invalid")
    exit(1)


def parse_config_or_exit(yml: Dict) -> Config:
    timezone = str(yml["timezone"])
    if yml["timezone"] not in pytz.all_timezones:
        logging.error("Timezone '%s' is invalid", yml["timezone"])
        exit(1)

    config: Config = {
        "username": str(yml["username"]) if "username" in yml else "admin",
        "password": str(yml["password"]),
        "location": astral.LocationInfo(
            name="custom",
            region="custom",
            timezone=timezone,
            latitude=float(yml["latitude"]),
            longitude=float(yml["longitude"]),
        ),
        "method": parse_method_or_exit(yml),
        "ipc": [],
    }

    for c in yml["ipc"]:
        ipc_config: ConfigIPC = {
            "ip": str(c["ip"]),
            "name": str(c["name"]) if "name" in c else str(c["ip"]),
            "username": str(c["username"]) if "username" in c else config["username"],
            "password": str(c["password"]) if "password" in c else config["password"],
            "channel": int(c["channel"]) if "channel" in c else 0,
            "method": parse_method_or_exit(c["method"])
            if "method" in c
            else config["method"],
        }

        config["ipc"].append(ipc_config)

    return config
