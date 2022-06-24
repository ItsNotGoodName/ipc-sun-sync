from datetime import time, datetime, timedelta
from enum import Enum
from typing import List, Protocol, Tuple, Union, TypedDict

import astral


class ConfigMethod(Enum):
    CGI = 0
    RPC = 1


class ConfigIPC(TypedDict):
    name: str
    ip: str
    username: str
    password: str
    channel: int
    method: ConfigMethod
    sunrise_offset: timedelta
    sunset_offset: timedelta


class Config(TypedDict):
    location: astral.LocationInfo
    ipc: List[ConfigIPC]


class SwitchMode(Enum):
    DAY = 0
    BRIGHTNESS = 1
    TIME = 2
    NIGHT = 3
    GENERAL = 4


class IPC(Protocol):
    def get_sunrise_and_sunset(self, channel=0) -> Tuple[time, time, SwitchMode]:
        raise NotImplemented

    def set_sunrise_and_sunset(
        self,
        sunrise: Union[datetime, time],
        sunset: Union[datetime, time],
        switch_mode=SwitchMode.TIME,
        channel=0,
    ) -> None:
        raise NotImplemented
