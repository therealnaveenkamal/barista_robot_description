#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_prefix

def generate_launch_description():

    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_box_bot_gazebo = get_package_share_directory('barista_robot_description')

    description_package_name = "barista_robot_description"
    install_dir = get_package_prefix(description_package_name)

    # Set the path to the WORLD model files. Is to find the models inside the models folder in my_box_bot_gazebo package
    gazebo_models_path = os.path.join(pkg_box_bot_gazebo, 'meshes')
    robot_path = os.path.join(pkg_box_bot_gazebo, "xacro", 'barista_robot_model_multiple.urdf.xacro')

    # os.environ["GAZEBO_MODEL_PATH"] = gazebo_models_path

    if 'GAZEBO_MODEL_PATH' in os.environ:
        os.environ['GAZEBO_MODEL_PATH'] =  os.environ['GAZEBO_MODEL_PATH'] + ':' + install_dir + '/share' + ':' + gazebo_models_path
    else:
        os.environ['GAZEBO_MODEL_PATH'] =  install_dir + "/share" + ':' + gazebo_models_path

    if 'GAZEBO_PLUGIN_PATH' in os.environ:
        os.environ['GAZEBO_PLUGIN_PATH'] = os.environ['GAZEBO_PLUGIN_PATH'] + ':' + install_dir + '/lib'
    else:
        os.environ['GAZEBO_PLUGIN_PATH'] = install_dir + '/lib'

    

    print("GAZEBO MODELS PATH=="+str(os.environ["GAZEBO_MODEL_PATH"]))
    print("GAZEBO PLUGINS PATH=="+str(os.environ["GAZEBO_PLUGIN_PATH"]))

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py'),
        )
    )

    robot_name_1 = "rick"
    robot_name_2 = "morty"

    robot_state_publisher_node1 = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher_node',
        namespace=robot_name_1,
        emulate_tty=True,
        parameters=[{
            'frame_prefix': robot_name_1+'/',
            'use_sim_time': True,
            'robot_description': Command(['xacro ', robot_path, ' include_laser:=', LaunchConfiguration('include_laser'), ' robot_name:=', robot_name_1])
        }],
        output="screen"
    )

    robot_state_publisher_node2 = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher_node',
        namespace=robot_name_2,
        emulate_tty=True,
        parameters=[{
            'frame_prefix': robot_name_2+'/',
            'use_sim_time': True,
            'robot_description': Command(['xacro ', robot_path, ' include_laser:=', LaunchConfiguration('include_laser'), ' robot_name:=', robot_name_2])
        }],
        output="screen"
    )


    rviz_config_dir = os.path.join(pkg_box_bot_gazebo, 'rviz', 'urdf_vis.rviz')


    rviz_node = Node(
            package='rviz2',
            executable='rviz2',
            output='screen',
            name='rviz_node',
            parameters=[{'use_sim_time': True}],
            arguments=['-d', rviz_config_dir])


    spawn_robot1 = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='spawn_entity_1',
        output='screen',
        arguments=['-entity', 'rick',
                   '-x', '4', '-y', '0', '-z', '0.2',
                   '-R', '0', '-P', '0', '-Y', '0',
                   '-topic', robot_name_1+'/robot_description'
                   ]
    )

    spawn_robot2 = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='spawn_entity_2',
        output='screen',
        arguments=['-entity', 'morty',
                   '-x', '4', '-y', '3', '-z', '0.2',
                   '-R', '0', '-P', '0', '-Y', '0',
                   '-topic', robot_name_2+'/robot_description'
                   ]
    )

    include_laser_arg = DeclareLaunchArgument(
        'include_laser',
        default_value='true',
        description='Include the laser scanner sensor'
    )

    static_tf_rick = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_transform_publisher_rick',
        output='screen',
        emulate_tty=True,
        arguments=['0', '0', '0', '0', '0', '0', 'world', 'morty/odom']
    )

    static_tf_morty = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_transform_publisher_morty',
        output='screen',
        emulate_tty=True,
        arguments=['0', '0', '0', '0', '0', '0', 'world', 'rick/odom']
    )


    return LaunchDescription([
    include_laser_arg,
        DeclareLaunchArgument(
          'world',
          default_value=[os.path.join(pkg_box_bot_gazebo, 'worlds', 'empty.world'), ''],
          description='SDF world file'),
        gazebo,
        robot_state_publisher_node1,
        robot_state_publisher_node2,
        spawn_robot1,
        spawn_robot2,
        rviz_node,
        static_tf_rick,
        static_tf_morty
    ])