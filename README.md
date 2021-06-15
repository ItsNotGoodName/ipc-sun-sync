# ipc-sun-sync
Syncs sunrise time and sunset time on Dahua IP Cameras.

## Example Usage
`config.yml`
```yml
---
latitude: 34.0522
longitude: -118.2437
timezone: "America/Los_Angeles"

username: admin
password: password

ipc:
  - ip: 192.168.1.108
  - ip: 192.168.1.109
```
The following command will sync the cameras located at `192.168.1.108` and
`192.168.1.109` using the username `admin` and the password `password` as the 
credentials. The sunrise and sunset will be calculated using the `latitude` 
and `longitude` variables, then it will be converted to your timezone using the
 `timezone` variable.
```
ipc-sun-sync -c config.yml
```
The following command will list all possible timezones.
```
ipc-sun-sync -T
```

## Todo
- add sunrise and sunset offsets
- add daemon mode
- add sync by toggle modes instead of schedule to daemon mode
- add windows service
- add gui
