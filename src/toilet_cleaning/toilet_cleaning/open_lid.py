"""Open Lid: opens the toilet lid."""


import rclpy
import DR_init
from rclpy.node import Node

ROBOT_ID = "dsr01"
ROBOT_MODEL = "m0609"

DR_init.__dsr__id = ROBOT_ID
DR_init.__dsr__model = ROBOT_MODEL

class OpenLid:
    def __init__(self,node):
        from DR_common2 import posx, posj
        self.node=node
        self.lid_point=[posj(-10.13,-2.14,75.49,-2.76,106.43,-92.76),# 변기 손잡이 위,
                        posj(-9.01,-2.77,90.70,-3.94,93.12,-92.78), #변기 손잡이 위치
                        posj(-6.70,2.64,70.35,-0.63,26.74,-94.18)   #변기 탈출 
                    ]  
    def run(self):
        from DSR_ROBOT2 import (
                    set_tool,
                    set_tcp,
                    movej,
                    movel,
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
        
        self.node.get_logger().info('run 함수 시작')
        self.gripper_open()
        self.node.get_logger().info("그리퍼 오픈")
        self.go_home()    
        self.node.get_logger().info("홈 위치 도달")     
        self.move2lid()
        self.node.get_logger().info("변기 손잡이로 이동")
        self.gripper_close()
        self.node.get_logger().info("손잡이 잡기") 
        self.node.get_logger().info("open_lid_start")
        self.open_lid_define()
        self.node.get_logger().info("open_lid_end")
        
        wait(0.5)
        self.go_home()
                     
    def gripper_open(self):
            from DSR_ROBOT2 import set_digital_output
            set_digital_output(1, 0)
            set_digital_output(2, 1)
    def gripper_close(self):
            from DSR_ROBOT2 import set_digital_output
            set_digital_output(1, 1)
            set_digital_output(2, 0)
    def go_home(self):
            from DSR_ROBOT2 import movej
            from DR_common2 import posj
            home = posj(0, 0, 50, 0, 90, 0)
            movej(home, vel=30, acc=30)
    def move2lid(self):
        from DSR_ROBOT2 import movej, wait


        self.node.get_logger().info("변기 손잡이 잡자")
        movej(self.lid_point[0], vel=30, acc=30)
        wait(1.0)
        movej(self.lid_point[1], vel=30, acc=30)
        wait(1.0)
    def open_lid_define(self):
        from DSR_ROBOT2 import movec, movej,task_compliance_ctrl, release_compliance_ctrl,wait,DR_BASE
        from DR_common2 import posx,posj
        self.node.get_logger().info("open_lid_define 시작")
        open_lid_pos = [posx(314.36,-47.50,501.14,139.07,-170.30,54.78),#중간의 중간위치
                        posx(323.31,-46.56,591.79,160.97,-157.50,77.04),# 중간정도 열린 위치
                        posx(364.37,-46,637.05,169.26,-142.28,84.49),# 거의 열린 위치
                        posx(472.72,-50.34,595.19,172.79,-119.58,85.17) # 완전히 열린 위치
                        ]
        task_compliance_ctrl(stx=[3000, 3000, 3000, 200, 200, 200], time=0.0)
        self.node.get_logger().info('컴플라이언스 ON')
        wait(0.5)
        self.node.get_logger().info('move_1 시작')
        movec(open_lid_pos[0], open_lid_pos[1], vel=30, acc=30, ref=DR_BASE)
        wait(0.5)
        self.node.get_logger().info(f'open_lid_pos[0]: {open_lid_pos[0]}')
        self.node.get_logger().info(f'open_lid_pos[1]: {open_lid_pos[1]}')
        self.node.get_logger().info('movec_1 완료')
        
        movec(open_lid_pos[1], open_lid_pos[2], vel=30, acc=30, ref=DR_BASE)
        wait(0.5)
        self.node.get_logger().info(f'open_lid_pos[1]: {open_lid_pos[1]}')
        self.node.get_logger().info(f'open_lid_pos[2]: {open_lid_pos[2]}')
        self.node.get_logger().info('movec_2 완료')
        
        movec(open_lid_pos[2], open_lid_pos[3], vel=30, acc=30, ref=DR_BASE)
        wait(0.5)
        self.node.get_logger().info(f'open_lid_pos[2]: {open_lid_pos[2]}')
        self.node.get_logger().info(f'open_lid_pos[3]: {open_lid_pos[3]}')
        self.node.get_logger().info('movec_3 완료')
        wait(0.5)
        self.gripper_open()
        movej(self.lid_point[2], vel=30, acc=30)
        wait(0.5)
        
        self.node.get_logger().info(f'open_lid_pos[3]: {open_lid_pos[3]}')
        self.node.get_logger().info('movej_4 완료')
        self.node.get_logger().info('컴플라이언스 OFF')
        release_compliance_ctrl()
        

        
    
            
        
        
    


def main(args=None):
    rclpy.init(args=args)
    node = rclpy.create_node("open_lid", namespace=ROBOT_ID)
    DR_init.__dsr__node = node
    node.get_logger().info("open_lid_start")
    try:
        open_lid = OpenLid(node)
        node.get_logger().info('클래스 저장')
        open_lid.run()
        

    finally:
        node.destroy_node()
        rclpy.shutdown()
    

if __name__ == '__main__':
    print("main_start")
    main()
