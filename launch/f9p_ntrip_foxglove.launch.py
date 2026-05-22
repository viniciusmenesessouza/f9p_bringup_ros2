import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.substitutions import EnvironmentVariable
from launch_xml.launch_description_sources import XMLLaunchDescriptionSource
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
                'uart1.baudrate': 115200,

                'frame_id': 'gps_sensor',

                'tmode3': 0,
                'publish.rxm.rtcm': True,

                'config_on_startup': False,
                'save_on_shutdown': False,

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

                'authenticate': True,
                'username': EnvironmentVariable('NTRIP_USERNAME'),
                'password': EnvironmentVariable('NTRIP_PASSWORD'),

                'rtcm_message_package': 'rtcm_msgs',
                'rtcm_frame_id': 'gps_sensor',

                'reconnect_attempt_max': 10,
                'reconnect_attempt_wait_seconds': 5,
                'rtcm_timeout_seconds': 4,
            }
        ],
    )

    foxglove_bridge = IncludeLaunchDescription(
        XMLLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('foxglove_bridge'),
                'launch',
                'foxglove_bridge_launch.xml',
            )
        ),
        launch_arguments={
            'port': '8765',
            'address': '0.0.0.0',
        }.items(),
    )

    return LaunchDescription([
        f9p_node,
        ntrip_node,
        foxglove_bridge,
    ])