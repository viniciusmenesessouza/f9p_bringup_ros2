# F9P Bringup ROS2

ROS 2 Kilted bringup package for a u-blox F9P GNSS receiver with NTRIP corrections and live visualization through Foxglove.

The package is intended for a rover receiver connected through a stable udev alias, for example:

```text
/dev/ttyF9P
```

It includes launch support for:

- u-blox F9P receiver through `ublox_gps`
- NTRIP RTCM correction input through `ntrip_client`
- Foxglove Bridge for live map and numeric plots
- optional RViz satellite visualization, if configured in the package

## Tested target

```text
ROS 2: Kilted
GNSS: u-blox F9P
Serial device: /dev/ttyF9P
Baudrate: 115200
Fix topic: /f9p/fix
Foxglove bridge: ws://127.0.0.1:8765 (or 0.0.0.0:8765)
```

## Dependencies

Install the ROS 2 packages:

```bash
sudo apt update
sudo apt install \
  ros-kilted-ublox-gps \
  ros-kilted-ntrip-client \
  ros-kilted-rtcm-msgs \
  ros-kilted-foxglove-bridge \
  python3-colcon-common-extensions
```

Optional RViz satellite packages:

```bash
sudo apt install \
  ros-kilted-rviz2 \
  ros-kilted-rviz-satellite \
  ros-kilted-tf2-ros
```

## Workspace setup

Create a workspace and clone the package:

```bash
mkdir -p ~/f9p_ws/src
cd ~/f9p_ws/src

git clone <your-repository-url> f9p_bringup
```

Build:

```bash
cd ~/f9p_ws
colcon build --symlink-install
source install/setup.bash
```

## Udev rule

The package includes a udev rule installer for creating a stable serial alias such as `/dev/ttyF9P`.

Run it once:

```bash
cd ~/f9p_ws
source install/setup.bash
ros2 run f9p_bringup install_udev_rule.sh
```

Then reconnect the GNSS receiver and check:

```bash
ls -l /dev/ttyF9P
```

If the device is not present, inspect the connected serial devices:

```bash
ls -l /dev/ttyUSB*
ls -l /dev/ttyACM*
```

Reloading udev manually can also help:

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

## NTRIP credentials

The launch file reads the NTRIP credentials from environment variables:

```bash
export NTRIP_USERNAME='your_username'
export NTRIP_PASSWORD='your_password'
```

For persistent credentials, a local shell file can be used:

```bash
nano ~/.f9p_ntrip_env
```

Example content:

```bash
export NTRIP_USERNAME='your_username'
export NTRIP_PASSWORD='your_password'
```

Load it before launching:

```bash
source ~/.f9p_ntrip_env
```

## Launch F9P, NTRIP, and Foxglove

```bash
cd ~/f9p_ws
source install/setup.bash

source ~/.f9p_ntrip_env
ros2 launch f9p_bringup f9p_foxglove.launch.py
```

Or, if the credentials are set in the current shell:

```bash
ros2 launch f9p_bringup f9p_foxglove.launch.py
```

The Foxglove bridge should report:

```text
Server listening on port 8765
```

Expected advertised topics include:

```text
/f9p/fix
/f9p/navpvt
/f9p/navstatus
/f9p/rxmrtcm
/rtcm
```

## Foxglove connection

Open Foxglove Web and connect to:

```text
ws://127.0.0.1:8765 (or 0.0.0.0:8765)
```

If Foxglove runs on another machine, use the robot IP instead:

```text
ws://<robot_ip>:8765
```

The robot IP can be checked with:

```bash
hostname -I
```

## Foxglove map panel

Add a **Map** panel.

Use the GNSS fix topic:

```text
/f9p/fix
```

Suggested map settings:

```text
Base layer: Satellite
Point style: Pin or Square
Point size: 18-25 px
Follow topic: /f9p/fix
Time range: Last 60 s
```

The `/f9p/fix` message is `sensor_msgs/msg/NavSatFix`. The fields used by Foxglove are:

```text
latitude
longitude
altitude
```

## Foxglove plots

Add three **Plot** panels.

Latitude:

```text
/f9p/fix.latitude
```

Longitude:

```text
/f9p/fix.longitude
```

Altitude:

```text
/f9p/fix.altitude
```

Suggested plot settings:

```text
X-axis: Timestamp
Timestamp source: header.stamp
Window: sliding
Window size: 60 s
Show legend: enabled
Show values: enabled
```

## Check ROS topics

List topics:

```bash
ros2 topic list
```

Check the fix topic type:

```bash
ros2 topic info /f9p/fix
```

Check one fix message:

```bash
ros2 topic echo /f9p/fix --once
```

Expected structure:

```yaml
header:
  stamp:
    sec: ...
    nanosec: ...
  frame_id: ...
status:
  status: ...
  service: ...
latitude: ...
longitude: ...
altitude: ...
position_covariance: [...]
position_covariance_type: ...
```

## Check NTRIP and RTCM

Check if RTCM corrections are being published:

```bash
ros2 topic echo /rtcm
```

Check if the F9P driver sees RTCM information:

```bash
ros2 topic echo /f9p/rxmrtcm
```

Check receiver status:

```bash
ros2 topic echo /f9p/navstatus
```

Check the high-level navigation solution:

```bash
ros2 topic echo /f9p/navpvt
```

## Common issues

### Foxglove says localhost is unreachable

First check that the bridge is listening:

```bash
ss -ltnp | grep 8765
```

If needed, run the bridge alone:

```bash
ros2 launch foxglove_bridge foxglove_bridge_launch.xml port:=8765 address:=127.0.0.1 #(or 0.0.0.0)
```

Then connect Foxglove to:

```text
ws://127.0.0.1:8765 (or 0.0.0.0:8765)
```

If the web version works and the desktop app does not, the ROS side is already functioning. Use the web version or check the desktop app installation/sandboxing.

### Bind Error on port 8765

Check what is using the port:

```bash
sudo ss -ltnp | grep ':8765'
```

Stop the existing process or use another port, for example:

```bash
ros2 launch foxglove_bridge foxglove_bridge_launch.xml port:=8766 address:=127.0.0.1 #(or 0.0.0.0)
```

Then connect to:

```text
ws://127.0.0.1:8766 (or 0.0.0.0:8766)
```

### No `/f9p/fix`

Check that the serial device exists:

```bash
ls -l /dev/ttyF9P
```

Check whether the node is running:

```bash
ros2 node list
```

Check all GNSS-related topics:

```bash
ros2 topic list | grep -E 'fix|nav|ublox|f9p'
```

### Permission denied on the serial port

Add the user to the dialout group:

```bash
sudo usermod -a -G dialout $USER
```

Log out and log back in, then reconnect the device.

### No RTK fixed solution

Check the following:

```bash
ros2 topic echo /rtcm
ros2 topic echo /f9p/rxmrtcm
ros2 topic echo /f9p/navstatus
ros2 topic echo /f9p/navpvt
```

Typical causes are wrong mountpoint, unavailable caster, weak sky visibility, bad antenna placement, wrong correction stream, or no RTCM reaching the receiver.

## Repository layout

Expected package structure:

```text
f9p_bringup/
├── CMakeLists.txt
├── package.xml
├── launch/
│   ├── f9p_foxglove.launch.py
│   └── f9p_satellite.launch.py
├── rviz/
│   └── f9p_satellite.rviz
├── scripts/
│   └── install_udev_rule.sh
└── udev/
    └── 99-ublox-gps.rules
```

## Notes

The F9P launch uses the receiver as a rover, with `tmode3` disabled.

The NTRIP client publishes RTCM corrections on `/rtcm`.

The u-blox driver consumes RTCM corrections and publishes the GNSS solution on `/f9p/fix`.

Foxglove can use `/f9p/fix` directly for both the satellite map and latitude/longitude/altitude plots.
