# F9P Bringup

ROS 2 Kilted bringup package for a u-blox F9P GNSS receiver with NTRIP RTCM corrections and live visualization through Foxglove or RViz.

The package is intended for a rover setup where the F9P is connected through a serial device such as `/dev/ttyF9P`, receives RTCM corrections from an NTRIP caster, and publishes GNSS data as ROS 2 topics.

## Features

- ROS 2 launch for u-blox F9P.
- NTRIP client integration for RTCM correction input.
- udev rule installation for stable serial naming.
- Foxglove Bridge launch for browser-based satellite map visualization.
- Optional RViz satellite-map visualization.
- Publishes standard GNSS topics such as `/fix`, `/f9p/fix`, `/f9p/navpvt`, `/f9p/navstatus`, and `/f9p/rxmrtcm`.

## Tested environment

- Ubuntu 24.04
- ROS 2 Kilted
- u-blox F9P receiver
- `ublox_gps`
- `ntrip_client`
- `foxglove_bridge`
- `rtcm_msgs`

## Repository layout

```text
f9p_bringup/
├── CMakeLists.txt
├── package.xml
├── launch/
│   ├── f9p_ntrip.launch.py
│   ├── f9p_satellite.launch.py
│   └── f9p_foxglove.launch.py
├── rviz/
│   └── f9p_satellite.rviz
├── scripts/
│   └── navsatfix_plot_markers.py
└── udev/
    ├── 99-ublox-gps.rules
    └── install_udev_rule.sh
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
  ros-kilted-rviz2 \
  ros-kilted-rviz-satellite \
  ros-kilted-tf2-ros \
  python3-colcon-common-extensions
```

If a package is not available through `apt`, clone the corresponding source package into the workspace `src/` folder and build it with `colcon`.

## Workspace setup

```bash
mkdir -p ~/f9p_ws/src
cd ~/f9p_ws/src

git clone <your-repository-url> f9p_bringup

cd ~/f9p_ws
colcon build --symlink-install
source install/setup.bash
```

To avoid sourcing manually every time:

```bash
echo "source ~/f9p_ws/install/setup.bash" >> ~/.bashrc
```

## udev setup

The package includes a udev rule installer for stable serial device naming.

Run once:

```bash
ros2 run f9p_bringup install_udev_rule.sh
```

Or run the script directly:

```bash
cd ~/f9p_ws/src/f9p_bringup/udev
./install_udev_rule.sh
```

Then unplug and reconnect the GNSS receiver.

Check that the device exists:

```bash
ls -l /dev/ttyF9P
```

If the device does not appear, inspect USB serial devices:

```bash
ls -l /dev/ttyACM*
ls -l /dev/ttyUSB*
udevadm info -a -n /dev/ttyACM0
```

Adjust `99-ublox-gps.rules` if your receiver exposes a different vendor/product ID or serial string.

## NTRIP credentials

Do not hardcode credentials in the launch file. Export them as environment variables:

```bash
export NTRIP_USERNAME='your_username'
export NTRIP_PASSWORD='your_password'
```

For persistent credentials, add them to a local shell file that is not committed to Git, for example:

```bash
nano ~/.f9p_ntrip_env
```

```bash
export NTRIP_USERNAME='your_username'
export NTRIP_PASSWORD='your_password'
```

Then load it before launching:

```bash
source ~/.f9p_ntrip_env
```

## Launch F9P + NTRIP

```bash
ros2 launch f9p_bringup f9p_ntrip.launch.py
```

This starts:

- `ublox_gps_node`
- `ntrip_ros.py`

Useful topic checks:

```bash
ros2 topic list
ros2 topic echo /f9p/fix --once
ros2 topic echo /f9p/navpvt --once
ros2 topic echo /f9p/navstatus --once
ros2 topic echo /rtcm --once
```

Expected GNSS fix message type:

```bash
ros2 topic info /f9p/fix
```

Expected type:

```text
sensor_msgs/msg/NavSatFix
```

The relevant fields are:

```text
latitude
longitude
altitude
position_covariance
status.status
status.service
```

## Launch with Foxglove

```bash
ros2 launch f9p_bringup f9p_foxglove.launch.py
```

This starts:

- F9P node
- NTRIP client
- Foxglove Bridge

Open Foxglove Web and connect to:

```text
ws://127.0.0.1:8765
```

If Foxglove is running on another machine, use the robot IP instead:

```text
ws://<robot_ip>:8765
```

Get the robot IP with:

```bash
hostname -I
```

### Foxglove map panel

Add a **Map** panel and select:

```text
/f9p/fix
```

Recommended map settings:

```text
Base layer: Satellite
Point style: Pin or Square
Point size: 18–25 px
Follow topic: /f9p/fix
Time range: last 60 seconds
```

### Foxglove plots

Add three **Plot** panels:

```text
/f9p/fix.latitude
/f9p/fix.longitude
/f9p/fix.altitude
```

Recommended plot settings:

```text
X axis: timestamp
Timestamp source: header.stamp
Window: sliding
Window size: 60 s
Show legend: true
Show values: true
```

## Launch with RViz satellite map

```bash
ros2 launch f9p_bringup f9p_satellite.launch.py
```

This starts:

- F9P node
- NTRIP client
- static TF from `map` to `gps_sensor`
- RViz with satellite map configuration

RViz expects the GNSS fix topic:

```text
/f9p/fix
```

The RViz config is stored in:

```text
rviz/f9p_satellite.rviz
```

## Serial port configuration

The default launch expects:

```text
/dev/ttyF9P
```

If using a different serial device, edit the launch file parameter:

```python
'device': '/dev/ttyF9P'
```

The default baudrate is:

```text
115200
```

The launch also sets:

```python
'uart1.baudrate': 115200
```

## Common checks

### Check whether the F9P node is publishing fixes

```bash
ros2 topic echo /f9p/fix --once
```

### Check RTCM correction input

```bash
ros2 topic echo /rtcm --once
ros2 topic echo /f9p/rxmrtcm --once
```

### Check NTRIP logs

Run the launch and inspect whether the NTRIP node connects to the caster and receives correction data.

```bash
ros2 launch f9p_bringup f9p_foxglove.launch.py
```

### Check Foxglove Bridge

```bash
ss -ltnp | grep 8765
```

Expected:

```text
LISTEN ... 127.0.0.1:8765 ...
```

Test the socket:

```bash
nc -vz 127.0.0.1 8765
```

Expected:

```text
Connection to 127.0.0.1 8765 port [tcp/*] succeeded!
```

If port `8765` is already in use:

```bash
sudo ss -ltnp | grep ':8765'
sudo fuser -k 8765/tcp
```

Or change the Foxglove Bridge port in the launch file.

## Troubleshooting

### Foxglove Web works but Foxglove Desktop does not

Use Foxglove Web with:

```text
ws://127.0.0.1:8765
```

If the Web version works, the ROS bridge is working. The issue is isolated to the desktop app environment or its network access.

### Foxglove says localhost is unreachable

Use the explicit IPv4 address:

```text
ws://127.0.0.1:8765
```

instead of:

```text
ws://localhost:8765
```

### Foxglove Bridge bind error

If the bridge prints:

```text
Couldn't initialize websocket server: Bind Error
```

then the selected port is already in use or the address cannot be bound.

Check:

```bash
sudo ss -ltnp | grep ':8765'
```

Kill the existing process if needed:

```bash
sudo fuser -k 8765/tcp
```

Then relaunch.

### No `/dev/ttyF9P`

Reload udev rules:

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Then reconnect the receiver.

Check raw devices:

```bash
ls -l /dev/ttyACM*
ls -l /dev/ttyUSB*
```

### No RTK fix

Check:

```bash
ros2 topic echo /rtcm --once
ros2 topic echo /f9p/rxmrtcm --once
ros2 topic echo /f9p/navstatus --once
ros2 topic echo /f9p/navpvt --once
```

Possible causes:

- NTRIP caster unreachable.
- Wrong mountpoint.
- Wrong NTRIP credentials.
- RTCM stream not compatible with the receiver.
- Poor sky visibility.
- Receiver configuration not accepting RTCM on the active port.
- Insufficient convergence time.

## Notes

- `NavSatFix.latitude` and `NavSatFix.longitude` are in degrees.
- `NavSatFix.altitude` is in meters.
- `/f9p/fix` is the main topic for map visualization.
- `/f9p/navpvt` is useful for detailed u-blox navigation status.
- `/f9p/rxmrtcm` is useful for checking whether RTCM messages are being received.
- Foxglove does not need a custom plotting node for latitude, longitude, or altitude; it can plot those fields directly from `/f9p/fix`.

## License

Add your license here.
