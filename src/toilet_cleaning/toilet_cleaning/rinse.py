"""Rinse: rinses the toilet bowl with water."""




import rclpy
import DR_init

ROBOT_ID = "dsr01"
ROBOT_MODEL = "m0609"

DR_init.__dsr__id = ROBOT_ID
DR_init.__dsr__model = ROBOT_MODEL


class Rinse:
    def __init__(self, node, vel=30, acc=30):
        self.node = node
        self.vel = vel
        self.acc = acc
        # 좌표는 setup_robot()에서 posx/posj가 바인딩된 후 생성

    def setup_robot(self, dsr, posx, posj):
        # 로봇 제어 함수 바인딩
        self.movej = dsr.movej
        self.movel = dsr.movel
        self.movec = dsr.movec
        self.movesj = dsr.movesj
        self.set_digital_output = dsr.set_digital_output
        self.wait = dsr.wait
        self.get_current_posx = dsr.get_current_posx
        self.task_compliance_ctrl = dsr.task_compliance_ctrl
        self.set_stiffnessx = dsr.set_stiffnessx
        self.set_desired_force = dsr.set_desired_force
        self.release_force = dsr.release_force
        self.release_compliance_ctrl = dsr.release_compliance_ctrl
        self.amove_periodic = dsr.amove_periodic
        self.set_velj = dsr.set_velj
        self.set_accj = dsr.set_accj
        self.set_velx = dsr.set_velx
        self.set_accx = dsr.set_accx
        self.DR_BASE = dsr.DR_BASE
        self.DR_FC_MOD_ABS = dsr.DR_FC_MOD_ABS

        # posx/posj가 준비된 시점에 좌표 생성
        self.bleach_grip1 = posj(-22.68,12.59,102.65,50.78,93.78,-14.85)# 샤워기 위
        self.bleach_grip2 = posj(4.18,10.22,94.84,35.89,81.23,-1.18)# 샤워기 잡는 위치
        self.bleach_grip_up = posj(5.54,1.50,80.15,34.02,91.07,16.72)# 샤워기 들어올릴 위치
        self.bleach_grup_dn= posj(6.95,1.99,85.36,32.91,86.04,13.82) # 샤워기 제자리 안전위치
        # 변기 위에 샤워기 들고 있을 posj값
        self.bleach_home = posj(0.0, -10.5, 50.0, 0.0, 90.0, -90.0)
        # 변기 좌표 4개(샤워기 돌릴 위치)
        self.bleach_start = posj(-0.01, -36.50, 78.55, -5.84, 82.43 , -90.01)
        self.bleach_via1 = posj(35.46, 7.06, 34.84, -28.72, 108.65, -83.72)
        self.bleach_half = posj(3.82, 20.41, 15.44, -16.64, 101.7, -83.72)
        self.bleach_via2 = posj(-34.93, 14.96, 31.92, 14.75, 102.92, -83.72)
        # 우리 모두의 홈좌표
        self.our_base = posj(0, 0, 50, 0, 90, 0)
    # 전체 함수 동작 함수
    def run(self):
        self.node.get_logger().info("rinse...")
        self.gripper_open()
        self.node.get_logger().info("그리퍼 오픈완료")
        self.go_gripper_home()
        self.grip_bleach()
        self.go_gripper_home()
        self.apply()
        self.go_gripper_home()
        self.release_bleach()
        self.wait(1.0)
        self.go_to_base()
        

    # 샤워기를 잡으러 감
    def grip_bleach(self):
        self.node.get_logger().info("Grip_bleach")
        self.gripper_open()
        self.movej(self.bleach_grip1, vel=self.vel, acc=self.acc)
        self.wait(1.0)
        self.movej(self.bleach_grip2, vel=self.vel, acc=self.acc)
        self.wait(1.0)
        self.gripper_close()
        self.movej(self.bleach_grip_up, vel=self.vel, acc=self.acc)
        self.wait(1.0)

    # 락스를 돌려두기 위해 감
    def release_bleach(self):
        self.node.get_logger().info("Release_bleach")
        self.movej(self.bleach_grip_up, vel=self.vel, acc=self.acc)
        self.wait(1.5)
        self.movej(self.bleach_grup_dn,vel=10,acc=10)
        self.task_compliance_ctrl()
        self.set_stiffnessx(
            [3000, 3000, 3000, 200, 200, 200],
            time=0.0
        )
        self.set_desired_force(
            [0, 0, -50, 0, 0, 0],
            [0, 0, 1, 0, 0, 0],
            time=0.0,
            mod=self.DR_FC_MOD_ABS
        )
        self.wait(9.0)
        self.release_force(time=0.0)
        self.release_compliance_ctrl()
        self.wait(1.0)
        self.gripper_open()

    # 그리퍼 오픈
    def gripper_open(self):
        self.node.get_logger().info("gripper_open")
        self.set_digital_output(1, 0)
        self.set_digital_output(2, 1)
        self.wait(1.0)

    # 그리퍼 닫기
    def gripper_close(self):
        self.node.get_logger().info("gripper_close")
        self.set_digital_output(1, 1)
        self.set_digital_output(2, 0)
        self.wait(1.0)

    # 세제 홈 위치 (실제 홈 위치와 그리퍼 각도 다름)
    def go_gripper_home(self):
        self.node.get_logger().info("go_bleach_home")
        self.movej(self.bleach_home, vel=self.vel, acc=self.acc)
        self.wait(1.0)

    # 도포하는 시작 위치로 이동
    def move_to_start(self):
        self.node.get_logger().info("move_to_start")
        self.movej(self.bleach_start, vel=self.vel, acc=self.acc)
        self.wait(1.0)

    # 세제를 실제로 도포
    def apply(self):
        self.node.get_logger().info("apply")
        self.move_to_start()
        self.wait(1.0)
        current = self.get_current_posx()

        bleach_waypoint = [
            self.bleach_start,
            self.bleach_via1,
            self.bleach_half,
            self.bleach_via2,
            self.bleach_start
        ]

        self.movesj(bleach_waypoint, vel=self.vel, acc=self.acc)
        self.wait(1.0)
        
        return True

    def go_to_base(self):
        self.node.get_logger().info("go_to_base")
        self.movej(self.bleach_grip_up, vel=self.vel, acc=self.acc)
        self.wait(1.0)
        self.movej(self.our_base, vel=self.vel, acc=self.acc)

def main(args=None):
    rclpy.init(args=args)
    node = rclpy.create_node("rinse", namespace=ROBOT_ID)
    DR_init.__dsr__node = node

    try:
        import DSR_ROBOT2 as dsr
        from DR_common2 import posx, posj
        bleach = Rinse(node)
        bleach.setup_robot(dsr, posx, posj)
        bleach.run()
    except Exception:
        node.get_logger().error("Robot Error", exc_info=True)
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()