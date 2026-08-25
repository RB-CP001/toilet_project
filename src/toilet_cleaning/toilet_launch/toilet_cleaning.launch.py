import os
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    
    cleaning_manager_node = Node(
        package='toilrt_cleaning',
        executable='cleaning_manager',
        name='cleaning_manager_node',
        namespace='dsr01',
        output='screen'
    )

    # 노드들 반환
    return LaunchDescription([
        cleaning_manager_node
    ])
