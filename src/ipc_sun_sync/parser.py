import argparse
import pathlib
import sys
import logging

import yaml
from yaml import YAMLError
import pytz
from astral import LocationInfo

from . import __description__


def parse_args():
    parser = argparse.ArgumentParser(description=__description__)
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


def parse_yml(path):
    try:
        with path.open(mode="r") as stream:
            return yaml.safe_load(stream)
    except FileNotFoundError:
        logging.error("File '%s' does not exist", path)
    except PermissionError:
        logging.error("File '%s' is not readable", path)
    except YAMLError as error:
        logging.error(error)
    return False


def parse_config(yml):
    config = {}
    config["longitude"] = float(yml["longitude"])
    config["latitude"] = float(yml["latitude"])
    config["timezone"] = pytz.timezone(yml["timezone"])

    config["username"] = str(yml["username"])
    config["password"] = str(yml["password"])
    config["location"] = LocationInfo(
        "name",
        "region",
        config["timezone"],
        config["latitude"],
        config["longitude"],
    )

    config["ipc"] = []
    for c in yml["ipc"]:
        ipc = {}

        ipc["ip"] = str(c["ip"])
        ipc["name"] = str(c["name"]) if "name" in c else c["ip"]
        ipc["username"] = str(c["username"]) if "username" in c else yml["username"]
        ipc["password"] = str(c["password"]) if "password" in c else yml["password"]
        ipc["channel"] = int(c["channel"]) if "channel" in c else 0

        config["ipc"].append(ipc)
    return config
