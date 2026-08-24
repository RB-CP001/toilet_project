"""Apply Bleach: applies bleach to the toilet bowl."""

import rclpy
import DR_init

ROBOT_ID = "dsr01"
ROBOT_MODEL = "m0609"

DR_init.__dsr__id = ROBOT_ID
DR_init.__dsr__model = ROBOT_MODEL


class ApplyBleach:
    def __init__(self, node, vel=60, acc=60):
        self.node = node
        self.vel = vel
        self.acc = acc
        # 좌표는 setup_robot()에서 posx/posj가 바인딩된 후 생성

    def setup_robot(self, dsr, posx, posj):
        # 로봇 제어 함수 바인딩
        self.movej = dsr.movej
        self.movel = dsr.movel
        self.movec = dsr.movec
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
        self.bleach_grip1 = posx(351.52, 217.0, 520.38, 3.36, 139.35, 85.00)
        self.bleach_grip2 = posx(480.52, 217.0, 360.38, 3.36, 139.35, 85.00)
        self.bleach_grip_up = posx(480.52, 217.0, 612.0, 3.36, 139.35, 85.00)
        # 변기 위에 세제 들고 있을 posj값
        self.bleach_home = posj(0.0, 0.0, 50.0, 0.0, 90.0, 93.3)
        # 변기 좌표 4개(세제 돌릴 위치)
        self.bleach_start = posx(427.60, -7.93, 505.72, 40.41, -171.26, 135.89)
        self.bleach_via1 = posx(384.86, 30.47, 505.72, 37.27, -166.55, 126.64)
        self.bleach_half = posx(338.66, -0.33, 505.72, 38.02, -161.64, 131.44)
        self.bleach_via2 = posx(415.89, -38.78, 505.72, 38.53, -161.64, 137.57)
    
    # 전체 함수 동작 함수
    def run(self):
        self.node.get_logger().info("Applying bleach...")
        self.go_gripper_home()
        self.wait(1.0)
        self.grip_bleach()
        self.wait(1.0)
        self.apply()
        self.wait(1.0)
        self.go_gripper_home()
        self.wait(1.0)
        self.release_bleach()

    # 락스를 잡으러 감
    def grip_bleach(self):
        self.node.get_logger().info("Grip_bleach")
        self.movel(self.bleach_grip1, vel=self.vel, acc=self.acc)
        self.wait(2.0)
        self.movel(self.bleach_grip2, vel=self.vel, acc=self.acc)
        self.gripper_close()
        self.movel(self.bleach_grip_up, vel=self.vel, acc=self.acc)

    # 락스를 돌려두기 위해 감
    def release_bleach(self):
        self.node.get_logger().info("Release_bleach")
        self.movel(self.bleach_grip_up, vel=self.vel, acc=self.acc)
        self.wait(1.5)
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

    # 그리퍼 닫기
    def gripper_close(self):
        self.node.get_logger().info("gripper_close")
        self.set_digital_output(1, 1)
        self.set_digital_output(2, 0)

    # 세제 홈 위치 (실제 홈 위치와 그리퍼 각도 다름)
    def go_gripper_home(self):
        self.node.get_logger().info("go_bleach_home")
        self.movej(self.bleach_home, vel=self.vel, acc=self.acc)

    # 도포하는 시작 위치로 이동
    def move_to_start(self):
        self.node.get_logger().info("move_to_start")
        self.movel(self.bleach_start, vel=self.vel, acc=self.acc)

    # 세제를 실제로 도포
    def apply(self):
        self.node.get_logger().info("apply")
        self.move_to_start()
        self.wait(1.0)
        self.movec(self.bleach_via1, self.bleach_half, vel=self.vel, acc=self.acc)
        self.movec(self.bleach_via2, self.bleach_start, vel=self.vel, acc=self.acc)
        return True


def main(args=None):
    rclpy.init(args=args)
    node = rclpy.create_node("apply_bleach", namespace=ROBOT_ID)
    DR_init.__dsr__node = node

    try:
        import DSR_ROBOT2 as dsr
        from DR_common2 import posx, posj
        bleach = ApplyBleach(node)
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