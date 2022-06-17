# ipc-sun-sync

[![GitHub](https://img.shields.io/github/license/itsnotgoodname/ipc-sun-sync)](./LICENSE)
[![PyPI](https://img.shields.io/pypi/v/ipc-sun-sync)](https://pypi.org/project/ipc-sun-sync/)

Sync sunrise and sunset on Dahua IP Cameras.

## Usage

Create `config.yml` with the following content.

```yml
---
latitude: 34.0522
longitude: -118.2437
timezone: America/Los_Angeles

username: admin
password: password

ipc:
  - ip: 192.168.1.108
  - ip: 192.168.1.109
  - ip: 192.168.1.110
    name: FriendlyNameForLogging
    username: OverideDefaultUser
    password: OverideDefaultPassword123
    channel: 1
```

The following command will sync the cameras located at `192.168.1.108`, `192.168.1.109`, `192.168.1.110`.

```
ipc-sun-sync -c config.yml
```

`192.168.1.108` and `192.168.1.109` will use the credentials `admin` and `password`.

`192.168.1.110` will have it's `name`, `username`, `password`, and `channel` overridden.
`name` is used for logging. `channel` is what video channel you want to apply the sun time, default is `channel` 0.

The sunrise and sunset times will be calculated using the `latitude` and `longitude` variables, then it will be converted to your timezone using the `timezone` variable.

### Show Timezones

```
ipc-sun-sync -T
```

### Show Version

```
ipc-sun-sync -V
```

## Troubleshooting

If the program says it is successful but sunrise and sunset times do not change, try disabling `Smart Codec` if it is enabled.

## To Do

- Add sunrise and sunset offsets
