import os

import launch
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, ExecuteProcess
from launch_ros.actions import Node

from launch.launch_description_sources import PythonLaunchDescriptionSource

from ament_index_python import get_package_share_directory


# ros2 run rqt_image_view rqt_image_view /sensing/fwc/raw/image

# downloads the rosbag file from drop box
if not os.path.isdir("short-limit-line-10x4"):
    os.system("wget https://www.dropbox.com/s/ed5ohvuszg20e6u/short-limit-line-10x4.zip")
    os.system("unzip short-limit-line-10x4.zip")
    os.system("rm short-limit-line-10x4.zip")


def generate_launch_description():

    launch_description = LaunchDescription()
    play_bag = ExecuteProcess(
            cmd = ['ros2','bag', 'play' ,'short-limit-line-10x4/bag','-l', '--qos-profile-overrides-path', 'short-limit-line-10x4/reliability_override.yaml']
            )
    launch_description.add_action(play_bag)

    rqt_image_view = Node(
        package='rqt_image_view',
        namespace='',
        executable='rqt_image_view',
        name='rqt_image_view',
        parameters=[
             {"topic": "/sensing/fwc/raw/image"}
        ]
    )
    launch_description.add_action(rqt_image_view)

    # ------------
    # Launch Files
    # ------------

    return launch_description
