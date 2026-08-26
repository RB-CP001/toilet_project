import rclpy
import DR_init

ROBOT_ID = "dsr01"
ROBOT_MODEL = "m0609"

DR_init.__dsr__id = ROBOT_ID
DR_init.__dsr__model = ROBOT_MODEL

class DetectLid:
    def __init__(self,node):
        from DR_common2 import posx, posj
        self.node=node
        self.movejpoint=[
            posj(-5.59, 16.17, 54.01, -4.45, 106.05, -92.24),# 변기 뚜껑 위
            posj(-10.13,-2.14,75.49,-2.76,106.43,-92.76),# 변기 손잡이 위,
            posj(-9.01,-2.77,90.70,-3.94,93.12,-92.78), #변기 손잡이 위치
        ]  
            

        # node.get.logger().info(movepoint[0])
        #함수 모음
    def gripper_open(self): 
        from DSR_ROBOT2 import set_digital_output 
        set_digital_output(1, 0)
        set_digital_output(2, 1)
        
    def gripper_close(self):
        from DSR_ROBOT2 import set_digital_output
        set_digital_output(1, 1)
        set_digital_output(2, 0)

    def lift_down(self):
                #get_logger().info("Lift +20 mm in BASE Z")
        from DSR_ROBOT2 import get_current_posx, movel, DR_BASE
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
        # def move2lid(posx):
        #     movej(posx, vel=30, acc=30)
    def insert_with_force(self,periodic=False):
        from DSR_ROBOT2 import movej, wait, task_compliance_ctrl, set_stiffnessx, set_desired_force, release_force, release_compliance_ctrl, check_force_condition, DR_AXIS_Z, DR_FC_MOD_ABS, DR_BASE
        self.node.get_logger().info("insert_with_force 실행")
        task_compliance_ctrl()

        set_stiffnessx(
            [3000, 3000, 3000, 200, 200, 200],
            time=0.0
        )

        set_desired_force(
            [0, 0, -50, 0, 0, 0],
            [0, 0, 1, 0, 0, 0],
            time=0.0,
            mod=DR_FC_MOD_ABS
        )
        wait(5.5)
        fcon1 = check_force_condition(DR_AXIS_Z, max=20,ref=DR_BASE) 
        self.node.get_logger().info(f"fcon1:{fcon1}")
            #확인 후 변기뚜껑 위 위치로 이동
        movej(self.movejpoint[0], vel=30, acc=30)
        if fcon1 == -1:
            wait(1.0)
            release_force(time=0.0)
            release_compliance_ctrl()
            self.node.get_logger().info(f"fcon1:{fcon1}")

            self.node.get_logger().info("insert_with_force if 실행됨")
            return True
        else:
            wait(3.0)
            release_force(time=0.0)
            release_compliance_ctrl()
            self.node.get_logger().info(f"fcon1:{fcon1}")
            self.node.get_logger().info("insert_with_force else실행")
            self.go_home()
            return False
                
            
        


            

    def go_home(self):
        from DSR_ROBOT2 import movej
        movej(self.home, vel=30, acc=30)

        
    def run(self):
        from DSR_ROBOT2 import (
            set_tool,
            set_tcp,
            movej,
            movel,
            posx, posj,
            movesj,
            movec,
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
        self.home = posj(0, 0, 50, 0, 90, 0)
        
        self.movejpoint=[
            posj(-5.59, 16.17, 54.01, -4.45, 106.05, -92.24),# 변기 뚜껑 위
            posj(-10.13,-2.14,75.49,-2.76,106.43,-92.76),# 변기 손잡이 위,
            posj(-9.01,-2.77,90.70,-3.94,93.12,-92.78) #변기 손잡이 위치
        ]
        self.node.get_logger().info("무브 포인트 지정 완료")
        self.gripper_open()
        self.node.get_logger().info("그리퍼 오픈")
        self.go_home()
        self.node.get_logger().info("홈위치 도달")
        self.gripper_close()
        self.node.get_logger().info("그리퍼 닫기")
        movej(self.movejpoint[0], vel=30, acc=30)
        self.insert_with_force()
        self.go_home()
        # def openlid(self, islid):
        #     from DSR_ROBOT2 import movej, movec, task_compliance_ctrl, release_compliance_ctrl, wait, DR_BASE,node
        #     if(islid==-1):
        #         #뚜껑을 열어라
        #         node.get_logger().info("openlid 실행됨")
        #         self.gripper_open()
        #         movej(self.movejpoint[1], vel=30, acc=30)
        #         movej(self.movejpoint[2], vel=30, acc=30)
        #         self.gripper_close()
        #         task_compliance_ctrl(stx=[3000, 3000, 3000, 200, 200, 200], time=0.0)
        #         movec(self.open_lid_pos[0], self.open_lid_pos[1], vel=30, acc=30, ref=DR_BASE)
        #         release_compliance_ctrl()
        # try:
        #     print("detect_lid_start")
        #     self.gripper_open()
        #     self.go_home()
        #     self.gripper_close()
            
        #     movej(self.movejpoint[0], vel=30, acc=30)
        #     islid = self.insert_with_force()
        #     wait(1.0)
        #     node.get_logger().info(f"뚜껑 : {islid}")
        
        #     self.openlid(islid)
        #     node.get_logger().info("openlid")

        # finally:
        #     node.destroy_node()
        #     rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)
    node = rclpy.create_node("detect_lid", namespace=ROBOT_ID)
    DR_init.__dsr__node = node
    try:
        node.get_logger().info("detect_lid_start")
        
        detect_lid = DetectLid(node)
        node.get_logger().info('클래스 저장')
        detect_lid.run()
        node.get_logger().info('detect_lid_run 완료')
    except Exception:
        node.get_logger().error("Robot Error", exc_info=True)
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