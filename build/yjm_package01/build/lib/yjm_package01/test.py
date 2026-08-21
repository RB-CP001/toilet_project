import rclpy
import DR_init

ROBOT_ID = "dsr01"
ROBOT_MODEL = "m0609"

DR_init.__dsr__id = ROBOT_ID
DR_init.__dsr__model = ROBOT_MODEL


def main(args=None):
    rclpy.init(args=args)

    node = rclpy.create_node("toilet_open", namespace=ROBOT_ID)
    DR_init.__dsr__node = node

    from DSR_ROBOT2 import (
        set_tool,
        set_tcp,
        movej,
        movel,
        set_digital_output,
        wait,
        get_current_posx,
        trans,
        task_compliance_ctrl,
        set_stiffnessx,
        set_desired_force,
        release_force,
        release_compliance_ctrl,
        amove_periodic,
        set_singularity_handling,
        check_force_condition,
        DR_BASE,
        DR_AVOID,
        DR_FC_MOD_ABS,
        DR_AXIS_Z,
    )

    from DR_common2 import posx, posj

    #변수 모음
    home = posj(0, 0, 50, 0, 90, 0)
    movepoint=[
        posj(0.46, 2.85, 66.71, -0.09, 110.23, 0.08),

    ]
    node.get.logger().info(movepoint[0])
    #함수 모음
    def gripper_open():  
            set_digital_output(1, 0)
            set_digital_output(2, 1)
    
    def gripper_close():
            set_digital_output(1, 1)
            set_digital_output(2, 0)
    def lift_down():
            #get_logger().info("Lift +20 mm in BASE Z")

            position, sol= get_current_posx(ref=DR_BASE)

            #get_logger().info(f"Current position: {position}, sol={sol}")

            move_point = [
                position[0],
                position[1],
                position[2] - 300,
                position[3],
                position[4],
                position[5],
            ]

            #get_logger().info(f"Lift target: {move_point}")

            movel(
                move_point,
                vel=10.0,
                acc=10.0,
                ref=DR_BASE
            )
            movel(move_point, vel=50, acc=20)

    def insert_with_force(periodic=False):
        task_compliance_ctrl()

        set_stiffnessx(
            [3000, 3000, 3000, 200, 200, 200],
            time=0.0
        )

        set_desired_force(
            [0, 0, -30, 0, 0, 0],
            [0, 0, 1, 0, 0, 0],
            time=0.0,
            mod=DR_FC_MOD_ABS
        )

        fcon1 = check_force_condition(DR_AXIS_Z, min=5, ref=DR_BASE) 

        #확인 후 변기뚜껑 위 위치로 이동
        move2lid()

        wait(3.0)

        release_force(time=0.0)
        release_compliance_ctrl()

        #변기 뚜껑이 있는지 없는지 반환
        return fcon1

    def home():
        movej(home, vel=30, acc=30)

    def move2lid():
         movej(movepoint[0], vel=30, acc=30)

    def openlid(islid):
         if(islid==True):
              #뚜껑을 열어라
              pass

    try:
        home()
        move2lid()
        islid = insert_with_force()
        # node.get_logger.info(f"뚜껑 : {islid}")
        openlid(islid)

    finally:
        node.destroy_node()
        rclpy.shutdown()




if __name__ == "__main__":
    
    main()
#ros2 launch m0609_rg2_bringup bringup.launch.py mode:=real host:=192.168.1.100 model:=m0609 port:=12345
# pkill -f ros2
# pkill -f gripper_joint_state_publisherls /dev/shm | grep fastrtps
# sudo rm -f /dev/shm/fastrtps_*pkill -9 -f "ros2"
# pkill -9 -f "ros2_control_node"
# pkill -9 -f "rviz2"
# pkill -9 -f "gripper"
# pkill -9 -f "robot_state_publisher"
# pkill -9 -f "joint_state_publisher"
# pkill -9 -f "static_transform_publisher"
# pkill -9 -f "run_emulator"ps aux | grep -E "ros2|dsr|gripper|rviz|run_emulator"