import re
import datetime

import requests
import requests.auth

from .exceptions import LoginError, RequestError

SWITCH_MODE_DAY = 0
SWITCH_MODE_BRIGHTNESS = 1
SWITCH_MODE_TIME = 2
SWITCH_MODE_NIGHT = 3
SWITCH_MODE_GENERAL = 4

NIGHT_OPTION_KEYS = [
    "SwitchMode",
    "SunriseHour",
    "SunriseMinute",
    "SunriseSecond",
    "SunsetHour",
    "SunsetMinute",
    "SunsetSecond",
]


class DahuaCgi:
    def __init__(self, ip: str, username: str, password: str):
        self.ip = ip
        self.auth = requests.auth.HTTPDigestAuth(username, password)

    def request(self, params: str) -> requests.Response:
        res = requests.get(
            f"http://{self.ip}/cgi-bin/configManager.cgi?{params}",
            auth=self.auth,
            timeout=10,
        )

        if res.status_code == 401:
            raise LoginError("Invalid credentials")

        if res.status_code != 200:
            raise RequestError(f"Unknown status code {res.status_code}")

        return res

    def get_night_options(self, channel=0) -> dict:
        res = self.request(
            f"action=getConfig&name=VideoInOptions[{channel}].NightOptions"
        )

        night_options = {}
        rows = re.findall("NightOptions\\.(.*)\r\n", res.text)
        for row in rows:
            key, value = row.split("=")
            if key in NIGHT_OPTION_KEYS:
                night_options[key] = int(value)

        for option in NIGHT_OPTION_KEYS:
            assert option in night_options

        return night_options

    def set_night_option(self, name: str, value: str, channel=0):
        self.request(
            f"action=setConfig&VideoInOptions[{channel}].NightOptions.{name}={value}"
        )

    def sync_sunrise_and_sunset(
        self,
        sunrise: datetime.datetime,
        sunset: datetime.datetime,
        switch_mode=SWITCH_MODE_TIME,
        channel=0,
    ) -> bool:
        night_options = self.get_night_options(channel=channel)

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
                self.set_night_option(k, v)
