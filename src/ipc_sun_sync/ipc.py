import logging
import re
import datetime
import typing

import requests
from requests.auth import HTTPDigestAuth

from .constants import SWITCH_MODE_TIME, NIGHT_OPTION_KEYS


def get_ipc(
    ip: str, auth: HTTPDigestAuth, url: str
) -> typing.Union[requests.Response, None]:
    try:
        res = requests.get(url, auth=auth, timeout=10)
    except requests.exceptions.RequestException:
        logging.error("Unable to connect to %s", ip)
        return None

    if res.status_code == 401:
        logging.error("Incorrect credentials for %s", ip)
        return None

    if res.status_code != 200:
        logging.error("Unknown status code %s from %s", res.status_code, ip)
        return None

    return res


def get_night_options(
    ip: str, auth: HTTPDigestAuth, channel=0
) -> typing.Union[dict, None]:
    res = get_ipc(
        ip,
        auth,
        f"http://{ip}/cgi-bin/configManager.cgi?action=getConfig&name=VideoInOptions[{channel}].NightOptions",
    )
    if not res:
        return None

    night_options = {}
    rows = re.findall("NightOptions\\.(.*)\r\n", res.text)
    for row in rows:
        try:
            key, value = row.split("=")
            if key in NIGHT_OPTION_KEYS:
                night_options[key] = int(value)
        except ValueError:
            logging.error("Invalid response from %s", ip)
            return None

    for option in NIGHT_OPTION_KEYS:
        if option not in night_options:
            logging.error("Response from %s is missing %s key", ip, option)
            return None

    return night_options


def set_night_option(ip: str, auth: HTTPDigestAuth, value: str, channel=0) -> bool:
    return not not get_ipc(
        ip,
        auth,
        f"http://{ip}/cgi-bin/configManager.cgi?action=setConfig&VideoInOptions[{channel}].NightOptions.{value}",
    )


def sync(
    ip: str,
    username: str,
    password: str,
    sunrise: datetime.datetime,
    sunset: datetime.datetime,
    switch_mode=SWITCH_MODE_TIME,
    channel=0,
) -> bool:
    auth = HTTPDigestAuth(username, password)
    night_options = get_night_options(ip=ip, auth=auth, channel=channel)
    if not night_options:
        return False

    state = {
        "SwitchMode": switch_mode,
        "SunriseHour": sunrise.hour,
        "SunriseMinute": sunrise.minute,
        "SunriseSecond": sunrise.second,
        "SunsetHour": sunset.hour,
        "SunsetMinute": sunset.minute,
        "SunsetSecond": sunset.second,
    }

    for k, v in state.items():
        if not night_options[k] == v:
            if not set_night_option(ip=ip, auth=auth, value=f"{k}={v}"):
                return False

    return True
