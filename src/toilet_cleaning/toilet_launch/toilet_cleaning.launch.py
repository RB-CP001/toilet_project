import os
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    
    # 1. 변기 뚜껑을 감지하는 노드 (DetectLid)
    detect_lid_node = Node(
        package='toilet_cleaning',      # package.xml에 적힌 패키지 이름
        executable='detect_lid',        # setup.py의 entry_points에 적은 실행 파일 이름
        name='detect_lid_node',         # ROS 2 네트워크 상에서 식별할 노드 이름
        namespace='dsr01',              # 로봇 네임스페이스
        output='screen'                 # 노드의 로그(get_logger)를 터미널 창에 바로 출력
    )

    # 2. 변기 뚜껑을 여는 노드 (OpenLid)
    open_lid_node = Node(
        package='toilet_cleaning',
        executable='open_lid',
        name='open_lid_node',
        namespace='dsr01',
        output='screen'
    )
    # 3. 락스 도포 노드 (ApplyBleach)
    apply_bleach_node = Node(
        package='toilet_cleaning',
        executable='apply_bleach',
        name='apply_bleach_node',
        namespace='dsr01',
        output='screen'
    )

    # 4. 브러시 청소 노드 (BrushClean)
    brush_clean_node = Node(
        package='toilet_cleaning',
        executable='brush_clean',
        name='brush_clean_node',
        namespace='dsr01',
        output='screen'
    )
    # 5. 샤워기 노드(Rinse)
    rinse_node = Node(
        package='toilet_cleaning',
        executable='rinse',
        name='rinse_node',
        namespace='dsr01',
        output='screen'
    )
    # 6. 종료 노드(Finish)
    finish_node = Node(
        package='toilet_cleaning',
        executable='finish',
        name='finish_node',
        namespace='dsr01',
        output='screen'
    )

    # 3. LaunchDescription에 생성한 노드들을 담아서 실행 대상으로 반환
    return LaunchDescription([
        detect_lid_node,
        open_lid_node,
        apply_bleach_node,
        brush_clean_node,
        rinse_node,
        finish_node
    ])
