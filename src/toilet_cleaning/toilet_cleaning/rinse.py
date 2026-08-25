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

        # 우리 모두의 홈 좌표
        self.our_base = posj(0, 0, 50, 0, 90, 0)
        # 샤워기를 2번에 걸쳐 잡으러가는 좌표
        self.rinse_grip1 = posj()
        self.rinse_grip2 = posj()
        # 샤워기 들어올린 좌표
        self.rinse_grip_up = posj()
        # 변기 좌표 4개 (샤워기로 내부 헹굴 때)
        self.rinse_start_inside = posj(-1.35, 8.13, 64.05, -6.94, 124.30, -83.79)
        self.rinse_via1 = posj(5.47, 19.90, 51.20, -8.61, 124.55, -83.72)
        self.rinse_half = posj(3.18, 29.13, 38.96, -15.90, 126.98, -83.71)
        self.rinse_via2 = posj(-0.25, 18.08, 54.38, -15.86, 123.52, -83.71)
        # 변기 외부 좌표 4개 (샤워기로 외부 헹굴 때)
        self.rinse_start_outside = posj()
        self.rinse_via1_outside = posj()
        self.rinse_half_outside = posj()
        self.rinse_via2_outside = posj()

    #전체 동작 함수
    def run(self):
        self.node.get_logger().info("Rinse run....")

    #샤워기를 잡으러 감
    def grip_rinse(self):
        self.node.get_logger().info("Grip_rinse")
        self.gripper_open()
        self.movej(self.rinse_grip1, vel=self.vel, acc=self.acc)
        self.wait(1.0)
        self.movej(self.rinse_grip2, vel=self.vel, acc=self.acc)
        self.wait(1.0)
        self.gripper_close()
        self.movej(self.rinse_grip_up, vel=self.vel, acc=self.acc)
        self.wait(1.0)

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

    # 샤워기로 내부를 헹구는 시작 위치로 이동
    def move_to_start_inside(self):
        self.node.get_logger().info("move_to_start_inside")
        self.movej(self.rinse_start_inside, vel=self.vel, acc=self.acc)
        self.wait(1.0)

    # 샤워기로 내부를 헹굼
    def rinse_inside(self):
        self.node.get_logger().info("rinse_inside")
        self.move_to_start()
        self.wait(1.0)
        current = self.get_current_posx()

        rinse_inside_waypoint1 = [
            self.rinse_start,
            self.rinse_via1,
            self.rinse_half,
        ]

        self.movesj(rinse_inside_waypoint, vel=self.vel, acc=self.acc)
        self.wait(1.0)
    
    # 샤워기로 외부를 헹구는 시작 위치로 이동
    def move_to_start_outside(self):
        self.node.get_logger().info("move_to_start_outside")
        self.movej(self.rinse_start_outside, vel=self.vel, acc=self.acc)
        self.wait(1.0)

    # 샤워기로 외부를 헹굼
    def rinse_outside(self):
        self.node.get_logger().info("rinse_inside")
        self.move_to_start()
        self.wait(1.0)
        current = self.get_current_posx()

        #왼쪽 절반 좌표
        rinse_outside_waypoint1 = [
            self.rinse_start_outside,
            self.rinse_via1_outside,
            self.rinse_half_outside,
        ]

        #오른쪽 절반 좌표
        rinse_outside_waypoint2 = [
            self.rinse_half_outside,
            self.rinse_via2_outside,
            self.rinse_start_outside
        ]

        self.movesj(rinse_outside_waypoint, vel=self.vel, acc=self.acc)
        self.wait(1.0)

    # 샤워기를 돌려두기 위해 감
    def release_rinse(self):
        self.node.get_logger().info("Release_rinse")
        self.movej(self.bleach_grip_up, vel=self.vel, acc=self.acc)
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
        self.wait(7.0)
        self.release_force(time=0.0)
        self.release_compliance_ctrl()
        self.wait(1.0)
        self.gripper_open()


    #우리 모두의 홈으로 이동
     def go_to_base(self):
        self.node.get_logger().info("go_to_base")
        self.movej(self.rinse_grip_up, vel=self.vel, acc=self.acc)
        self.wait(1.0)
        self.movej(self.our_base, vel=self.vel, acc=self.acc)




def main(args=None):
    rclpy.init(args=args)
    node = rclpy.create_node("rinse", namespace=ROBOT_ID)
    DR_init.__dsr__node = node

    try:
        import DSR_ROBOT2 as dsr
        from DR_common2 import posx, posj
        rinse = Rinse(node)
        rinse.setup_robot(dsr, posx, posj)
        rinse.run()
    except Exception:
        node.get_logger().error("Robot Error", exc_info=True)
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
