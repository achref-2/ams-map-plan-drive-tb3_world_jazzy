import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, ExecuteProcess, GroupAction,
                            IncludeLaunchDescription, RegisterEventHandler, TimerAction)
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
RVIZ = os.path.join(ROOT, 'rviz', 'exploration.rviz')
EXPLORE = os.path.join(ROOT, 'config', 'explore_params.yaml')
NAV2_PARAMS = os.path.join(ROOT, 'config', 'nav2_params.yaml')

# Warm-up: drive 0.6 m forward, then spin 360 deg, so SLAM sees around the start point
WARMUP = ("ros2 action send_goal /drive_on_heading nav2_msgs/action/DriveOnHeading "
          "'{target: {x: 0.6}, speed: 0.15, time_allowance: {sec: 15}}'; "
          "ros2 action send_goal /spin nav2_msgs/action/Spin '{target_yaw: 6.28}'")

def generate_launch_description():
    world = LaunchConfiguration('world')
    tb3 = get_package_share_directory('turtlebot3_gazebo')
    slam = get_package_share_directory('slam_toolbox')
    nav2 = get_package_share_directory('nav2_bringup')
    slam_params = os.path.join(slam, 'config', 'mapper_params_online_async.yaml')

    warmup = ExecuteProcess(cmd=['bash', '-c', WARMUP], output='screen',
                            condition=IfCondition(LaunchConfiguration('explore')))
    explore = Node(package='explore_lite', executable='explore', name='explore_node',
                   output='screen', parameters=[EXPLORE, {'use_sim_time': True}])

    return LaunchDescription([
        DeclareLaunchArgument('world', default_value='turtlebot3_world'),
        DeclareLaunchArgument('x_pose', default_value='-2.0'),
        DeclareLaunchArgument('y_pose', default_value='-0.5'),
        DeclareLaunchArgument('rviz', default_value='true'),
        DeclareLaunchArgument('explore', default_value='true'),

        GroupAction([IncludeLaunchDescription(PythonLaunchDescriptionSource(
            [os.path.join(tb3, 'launch', ''), world, '.launch.py']),
            launch_arguments={'x_pose': LaunchConfiguration('x_pose'),
                              'y_pose': LaunchConfiguration('y_pose')}.items())]),

        GroupAction([IncludeLaunchDescription(PythonLaunchDescriptionSource(
            os.path.join(slam, 'launch', 'online_async_launch.py')),
            launch_arguments={'use_sim_time': 'true',
                              'slam_params_file': slam_params}.items())]),

        GroupAction([IncludeLaunchDescription(PythonLaunchDescriptionSource(
            os.path.join(nav2, 'launch', 'navigation_launch.py')),
            launch_arguments={'use_sim_time': 'true',
                              'params_file': NAV2_PARAMS}.items())]),

        # Warm-up starts after 15 s; explore_lite starts only when warm-up is finished
        TimerAction(period=15.0, actions=[warmup]),
        RegisterEventHandler(OnProcessExit(target_action=warmup, on_exit=[explore])),

        Node(package='rviz2', executable='rviz2', arguments=['-d', RVIZ],
             parameters=[{'use_sim_time': True}], output='screen',
             condition=IfCondition(LaunchConfiguration('rviz'))),
    ])
