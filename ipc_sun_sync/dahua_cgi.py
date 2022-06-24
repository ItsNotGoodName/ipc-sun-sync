from datetime import datetime, time
from enum import Enum
from typing import Tuple, Union, TypedDict
import re

from requests.auth import HTTPDigestAuth
import requests

from .constants import SwitchMode
from .exceptions import LoginError, RequestError


class NightOption(TypedDict):
    SwitchMode: SwitchMode
    SunriseHour: int
    SunriseMinute: int
    SunriseSecond: int
    SunsetHour: int
    SunsetMinute: int
    SunsetSecond: int


class DahuaCgi:
    def __init__(self, ip: str, username: str, password: str):
        self.ip = ip
        self.auth = HTTPDigestAuth(username, password)

    def request(self, params: str) -> requests.Response:
        res = requests.get(
            f"http://{self.ip}/cgi-bin/configManager.cgi?{params}",
            auth=self.auth,
            timeout=10,
        )

        if res.status_code == 401:
            raise LoginError("invalid credentials")

        if res.status_code != 200:
            raise RequestError(f"unknown status code {res.status_code}")

        return res

    def get_night_options(self, channel=0) -> NightOption:
        res = self.request(
            f"action=getConfig&name=VideoInOptions[{channel}].NightOptions"
        )

        parsed = {}
        rows = re.findall("NightOptions\\.(.*)\r\n", res.text)
        for row in rows:
            key, value = row.split("=")
            parsed[key] = value

        night_options: NightOption = {
            "SunriseHour": int(parsed["SunriseHour"]),
            "SunriseMinute": int(parsed["SunriseMinute"]),
            "SunriseSecond": int(parsed["SunriseSecond"]),
            "SunsetHour": int(parsed["SunsetHour"]),
            "SunsetMinute": int(parsed["SunsetMinute"]),
            "SunsetSecond": int(parsed["SunsetSecond"]),
            "SwitchMode": SwitchMode(int(parsed["SwitchMode"])),
        }

        return night_options

    def set_night_option(self, name: str, value: str, channel=0):
        self.request(
            f"action=setConfig&VideoInOptions[{channel}].NightOptions.{name}={value}"
        )

    def get_sunrise_and_sunset(self, channel=0) -> Tuple[time, time, SwitchMode]:
        night_options = self.get_night_options(channel=channel)
        return (
            time(
                hour=night_options["SunriseHour"],
                minute=night_options["SunriseMinute"],
                second=night_options["SunriseSecond"],
            ),
            time(
                hour=night_options["SunsetHour"],
                minute=night_options["SunsetMinute"],
                second=night_options["SunsetSecond"],
            ),
            night_options["SwitchMode"],
        )

    def set_sunrise_and_sunset(
        self,
        sunrise: Union[datetime, time],
        sunset: Union[datetime, time],
        switch_mode=SwitchMode.TIME,
        channel=0,
    ):
        old_night_options = self.get_night_options(channel=channel)

        new_night_options: NightOption = {
            "SwitchMode": switch_mode,
            "SunriseHour": sunrise.hour,
            "SunriseMinute": sunrise.minute,
            "SunriseSecond": sunrise.second,
            "SunsetHour": sunset.hour,
            "SunsetMinute": sunset.minute,
            "SunsetSecond": sunset.second,
        }

        for k, v in new_night_options.items():
            if not old_night_options[k] == v:
                self.set_night_option(k, v.value if isinstance(v, Enum) else str(v))
