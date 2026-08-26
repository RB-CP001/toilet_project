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
        from DR_common2 import posj
        self.node=node
        self.lid_point=[posj(-10.13,-2.14,75.49,-2.76,106.43,-92.76),# 변기 손잡이 위,
                        posj(-9.01,-2.77,90.70,-3.94,93.12,-92.78), #변기 손잡이 위치
                        posj(-6.70,2.64,70.35,-0.63,26.74,-94.18)   #변기 탈출 
                    ]  
    def run(self):
        from DSR_ROBOT2 import wait
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
        from DSR_ROBOT2 import movej,task_compliance_ctrl, release_compliance_ctrl,wait
        from DR_common2 import posj
        self.node.get_logger().info("open_lid_define 시작")
        open_lid_pos = [posj(-9.03,4.32,77.37,-4.21,106.58,-92.78),#1번 열린 위치
                        posj(-10.22,9.07,66.39,-3.23,115.31,-92.84),#2번 열린위치
                        posj(-9.08,16.60,48.42,-4.76,127.22,-92.84),# 3번 열린위치
                        posj(-9.60,10.92,48.11,-2.11,117.35,-92.76), # 4번 열린위치
                        posj(-8.92,10.73,40.75,-1.55,108.02,-92.76), # 5번 열린 위치
                        posj(-7.50,11.97,39.42,-1.57,97.00,-92.76),# 6번 열린 위치
                        posj(-6.17,15.12,38.76,-1.21,85.98,-92.76), # 7번 열린 위치
                        posj(-6.60,18.61,38.75,0.87,77.30,-92.76)# 8번 열린 위치
                        
                        ]
        task_compliance_ctrl(stx=[3000, 3000, 3000, 200, 200, 200], time=0.0)
        self.node.get_logger().info('컴플라이언스 ON')
        wait(0.5)
        self.node.get_logger().info('move_1 시작')
        movej(open_lid_pos[0], vel=15, acc=15)
        wait(0.5)
        self.node.get_logger().info(f'open_lid_pos[0]: {open_lid_pos[0]}')
        
        self.node.get_logger().info('movej_1 완료')
        
        movej(open_lid_pos[1], vel=15, acc=15)
        wait(0.5)
        self.node.get_logger().info(f'open_lid_pos[1]: {open_lid_pos[1]}')
        
        self.node.get_logger().info('movej_2 완료')
        
        movej(open_lid_pos[2],  vel=15, acc=15)
        wait(0.5)
        self.node.get_logger().info(f'open_lid_pos[2]: {open_lid_pos[2]}')
        
        self.node.get_logger().info('movej_3 완료')
        wait(0.5)
        
        movej(open_lid_pos[3], vel=15, acc=15)
        wait(0.5)
        self.node.get_logger().info('movej_4 완료')
        movej(open_lid_pos[4], vel=15, acc=15)
        wait(0.5)
        self.node.get_logger().info('movej_5 완료')
        movej(open_lid_pos[5], vel=15, acc=15)
        wait(0.5)
        self.node.get_logger().info('movej_6 완료')
        movej(open_lid_pos[6], vel=15, acc=15)
        wait(0.5)
        self.node.get_logger().info('movej_7 완료')
        movej(open_lid_pos[7], vel=15, acc=15)
        wait(0.5)
        self.node.get_logger().info('movej_8 완료')
        self.gripper_open()
        self.node.get_logger().info('변뚜 후 그리퍼 오픈')
        movej(self.lid_point[2],vel=15,acc=15)

                
                
                
                
        
        self.node.get_logger().info(f'open_lid_pos[3]: {open_lid_pos[3]}')
        self.node.get_logger().info('movej_전부완료')
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

    except Exception:
        node.get_logger().error("Robot Error", exc_info=True)
        node.get_logger().error("Robot Error", exc_info=True)


    finally:
        node.destroy_node()
        rclpy.shutdown()
    

if __name__ == '__main__':
    print("main_start")
    main()
