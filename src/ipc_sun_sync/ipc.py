import logging
import re

import requests
from requests.auth import HTTPDigestAuth
from requests.exceptions import RequestException

from .constants import SWITCH_MODE_TIME, NIGHT_OPTION_KEYS


def get_ipc(ip, auth, url):
    try:
        res = requests.get(url, auth=auth, timeout=10)
    except RequestException:
        logging.error("Unable to connect to %s", ip)
        return False

    if res.status_code == 401:
        logging.error("Incorrect credentials for %s", ip)
        return False

    if res.status_code == 200:
        return res

    logging.error("Unknown status code %s from %s" % (res.status_code, ip))
    return False


def get_night_options(ip, auth, channel=0):
    url = (
        "http://%s/cgi-bin/configManager.cgi?action=getConfig&name=VideoInOptions[%s].NightOptions"
        % (ip, channel)
    )
    res = get_ipc(ip, auth, url)

    if not res:
        return False

    night_options = {}
    rows = re.findall("NightOptions\\.(.*)\r\n", res.text)
    for row in rows:
        try:
            key, value = row.split("=")
            if key in NIGHT_OPTION_KEYS:
                night_options[key] = int(value)
        except ValueError:
            logging.error("Invalid response from %s" % ip)
            return False

    for option in NIGHT_OPTION_KEYS:
        if option not in night_options:
            logging.error("Response from %s is missing %s key" % (ip, option))
            return False

    return night_options


def set_night_option(ip, auth, value, channel=0):
    url = (
        "http://%s/cgi-bin/configManager.cgi?action=setConfig&VideoInOptions[%s].NightOptions.%s"
        % (ip, channel, value)
    )

    return not not get_ipc(ip, auth, url)


def sync(
    ip,
    username,
    password,
    sunrise,
    sunset,
    switch_mode=SWITCH_MODE_TIME,
    channel=0,
):
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
