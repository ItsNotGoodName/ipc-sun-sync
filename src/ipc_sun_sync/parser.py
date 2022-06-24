import argparse
import pathlib
import sys
import logging

import astral
import pytz
import yaml

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


def parse_yml_or_exit(path):
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


def parse_config_or_exit(yml):
    if yml["timezone"] not in pytz.all_timezones:
        logging.error("Timezone '%s' is invalid", yml["timezone"])
        exit(1)

    config = {}
    config["username"] = str(yml["username"]) if "username" in yml else "admin"
    config["password"] = str(yml["password"])
    config["location"] = astral.LocationInfo(
        "name",
        "region",
        str(yml["timezone"]),
        float(yml["latitude"]),
        float(yml["longitude"]),
    )
    config["method"] = str(yml["method"]) if "method" in yml else "cgi"

    config["ipc"] = []
    for c in yml["ipc"]:
        ipc = {}

        ipc["ip"] = str(c["ip"])
        ipc["name"] = str(c["name"]) if "name" in c else c["ip"]
        ipc["username"] = str(c["username"]) if "username" in c else config["username"]
        ipc["password"] = str(c["password"]) if "password" in c else config["password"]
        ipc["channel"] = int(c["channel"]) if "channel" in c else 0
        ipc["method"] = str(c["method"]) if "method" in c else config["method"]

        config["ipc"].append(ipc)

    return config
