import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import EnvironmentVariable
from launch_ros.actions import Node


def generate_launch_description():
    f9p_node = Node(
        package='ublox_gps',
        executable='ublox_gps_node',
        name='ublox_f9p',
        namespace='f9p',
        output='screen',
        parameters=[
            {
                'device': '/dev/ttyF9P',
                'rate': 5.0,
                'frame_id': 'gps_sensor',

                # ROS 2 ublox_gps uses dotted parameter names.
                'uart1.baudrate': 115200,

                # Disabled TMODE3: rover mode, not fixed base/survey-in.
                'tmode3': 0,

                # RTCM input monitoring/publication.
                'publish.rxm.rtcm': True,

                'config_on_startup': False,
                'save_on_shutdown': False,

                # In ROS 2 this is numeric.
                # ublox_msgs/CfgDGNSS: RTK_FIXED = 3.
                'dgnss_mode': 3,

                'publish.nav.pvt': True,
                'publish.nav.status': True,
                'publish.nav.sat': True,
                'publish.nav.svinfo': False,
                'publish.mon.hw': True,
                'publish.nav.clock': False,
            }
        ],
    )

    ntrip_node = Node(
        package='ntrip_client',
        executable='ntrip_ros.py',
        name='ntrip_client',
        output='screen',
        parameters=[
            {
                'host': '193.137.94.71',
                'port': 2101,
                'mountpoint': 'IGP0',

                # ROS 2 ntrip_client uses "username", not ROS 1 "user".
                'authenticate': True,
                'username': EnvironmentVariable('NTRIP_USERNAME'),
                'password': EnvironmentVariable('NTRIP_PASSWORD'),

                'rtcm_message_package': 'rtcm_msgs',

                # Optional but useful.
                'rtcm_frame_id': 'gps',
                'reconnect_attempt_max': 10,
                'reconnect_attempt_wait_seconds': 5,
                'rtcm_timeout_seconds': 4,
            }
        ],
    )
    
    rviz_config = os.path.join(
        get_package_share_directory('f9p_bringup'),
        'rviz',
        'f9p_satellite.rviz',
    )

    static_gps_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='map_to_gps_sensor_tf',
        arguments=[
            '0', '0', '0',
            '0', '0', '0',
            'map',
            'gps_sensor',
        ],
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config],
    )

    return LaunchDescription([
        f9p_node,
        ntrip_node,
    ])