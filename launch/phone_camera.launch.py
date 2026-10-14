import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    config = os.path.join(
        get_package_share_directory('phone_camera'),
        'config',
        'phone_camera.yaml'
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'params_file',
            default_value=config,
            description='Parameter file (e.g. config/usb_camera.yaml)'
        ),
        Node(
            package='phone_camera',
            executable='phone_camera_node',
            name='phone_camera',
            output='screen',
            parameters=[LaunchConfiguration('params_file')],
        ),
        DeclareLaunchArgument(
            'view',
            default_value='false',
            description='Show the published image in a window'
        ),
        Node(
            package='phone_camera',
            executable='image_viewer_node',
            name='image_viewer',
            output='screen',
            condition=IfCondition(LaunchConfiguration('view')),
        ),
    ])

