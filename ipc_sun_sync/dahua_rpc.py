"""
Gist from https://gist.github.com/gxfxyz/48072a72be3a169bc43549e676713201

Basic Dahua RPC wrapper.

Example:
  from dahua_rpc import DahuaRpc

  dahua = DahuaRpc(host="192.168.1.10", username="admin", password="password")
  dahua.login()

  # Get the current time on the device
  print(dahua.current_time())

  # Set display to 4 grids with first view group
  dahua.set_split(mode=4, view=1)

  # Make a raw RPC request to get serial number
  print(dahua.request(method="magicBox.getSerialNo"))

Dependencies:
  pip install requests
"""

import hashlib
import datetime

import requests

from .exceptions import LoginError, RequestError


class DahuaRpc:
    def __init__(self, ip, username, password):
        self.ip = ip
        self.username = username
        self.password = password

        self.s = requests.Session()
        self.session_id = None
        self.id = 0

    def request(self, method, params=None, object_id=None, extra=None, url=None):
        """Make a RPC request."""
        self.id += 1
        data = {"method": method, "id": self.id}
        if params is not None:
            data["params"] = params
        if object_id:
            data["object"] = object_id
        if extra is not None:
            data.update(extra)
        if self.session_id:
            data["session"] = self.session_id
        if not url:
            url = "http://{}/RPC2".format(self.ip)
        r = self.s.post(url, json=data)
        return r.json()

    def login(self):
        """Dahua RPC login.

        Reversed from rpcCore.js (login, getAuth & getAuthByType functions).
        Also referenced:
        https://gist.github.com/avelardi/1338d9d7be0344ab7f4280618930cd0d
        """

        # login1: get session, realm & random for real login
        url = "http://{}/RPC2_Login".format(self.ip)
        method = "global.login"
        params = {
            "userName": self.username,
            "password": "",
            "clientType": "Dahua3.0-Web3.0",
        }
        r = self.request(method=method, params=params, url=url)

        self.session_id = r["session"]
        realm = r["params"]["realm"]
        random = r["params"]["random"]

        # Password encryption algorithm
        # Reversed from rpcCore.getAuthByType
        pwd_phrase = self.username + ":" + realm + ":" + self.password
        if isinstance(pwd_phrase, str):
            pwd_phrase = pwd_phrase.encode("utf-8")
        pwd_hash = hashlib.md5(pwd_phrase).hexdigest().upper()
        pass_phrase = self.username + ":" + random + ":" + pwd_hash
        if isinstance(pass_phrase, str):
            pass_phrase = pass_phrase.encode("utf-8")
        pass_hash = hashlib.md5(pass_phrase).hexdigest().upper()

        # login2: the real login
        params = {
            "userName": self.username,
            "password": pass_hash,
            "clientType": "Dahua3.0-Web3.0",
            "authorityType": "Default",
            "passwordType": "Default",
        }
        r = self.request(method=method, params=params, url=url)

        if r["result"] is False:
            raise LoginError(str(r))

    def set_config(self, params):
        """Set configurations."""

        method = "configManager.setConfig"
        r = self.request(method=method, params=params)

        if r["result"] is False:
            raise RequestError(str(r))

    def get_config(self, params):
        """Get configurations."""

        method = "configManager.getConfig"
        r = self.request(method=method, params=params)

        if r["result"] is False:
            raise RequestError(str(r))

        return r

    def sync_sunrise_and_sunset(
        self,
        sunrise: datetime.datetime,
        sunset: datetime.datetime,
        channel=0,
    ):
        table = self.get_config(params={"name": "VideoInMode"})["params"]["table"]
        table[0]["Config"] = [0, 1]
        table[0]["Mode"] = 1
        assert table[0]["TimeSection"][channel][0].startswith("1 ")
        table[0]["TimeSection"][channel][
            0
        ] = f"1 {sunrise.strftime('%H:%M:%S')}-{sunset.strftime('%H:%M:%S')}"
        self.set_config(params={"name": "VideoInMode", "table": table, "options": []})
