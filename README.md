# ipc-sun-sync

[![PyPI - License](https://img.shields.io/pypi/l/ipc-sun-sync)](./LICENSE)
[![PyPI](https://img.shields.io/pypi/v/ipc-sun-sync)](https://pypi.org/project/ipc-sun-sync/)

Sync sunrise and sunset on Dahua IP cameras.

## Usage

See [config.yml.def](./config.yml.def) for a starter configuration.

### Example

Create `config.yml` with the following content.

```yml
---
latitude: 34.0522
longitude: -118.2437
timezone: America/Los_Angeles

username: admin
password: password
method: cgi
sunrise_offset: "00:30:00"
sunset_offset: "-01:20:00"

ipc:
  - ip: 192.168.1.108
  - ip: 192.168.1.109
    sunset_offset: "00:20:00"
    method: rpc
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

Sunrise will be 30 minutes late and sunset will be 1 hour and 20 minutes early.

`192.168.1.108` and `192.168.1.109` will use the credentials `admin` and `password`.

`192.168.1.109` will interact through rpc instead of cgi and sunset will be 20 minutes late.

`192.168.1.110` will have it's `name`, `username`, `password`, and `channel` overridden.
`name` is used for logging. `channel` is the video channel you want to apply the sun times, default is 0.

The sunrise and sunset times will be calculated using the `latitude` and `longitude` variables, then it will be converted to your timezone using the `timezone` variable.

### Check Configuration

```
ipc-sun-sync -c config.yml --check
```

### Verify IPC Settings

Shows the sunrise time, sunset time, and switch mode currently on the IP cameras.

```
ipc-sun-sync -c config.yml --verify
```

### Show Timezones

```
ipc-sun-sync -T
```

### Show Version

```
ipc-sun-sync -V
```

## Changelog

[CHANGELOG.md](./CHANGELOG.md)

## Troubleshooting

- If the program says it is successful but the sunrise and sunset times do not change, ~~try disabling `Smart Codec` if it is enabled.~~ use rpc.

## To Do

- Add verbose logging.
