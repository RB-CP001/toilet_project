"""Finish: finalizes the cleaning sequence and reports completion."""

import rclpy
import DR_init

ROBOT_ID = "dsr01"
ROBOT_MODEL = "m0609"

DR_init.__dsr__id = ROBOT_ID
DR_init.__dsr__model = ROBOT_MODEL


class Finish:

    def __init__(self, node):
        self.node = node

        from DSR_ROBOT2 import (
            movej,
            wait,
            set_digital_output,
            task_compliance_ctrl,
            set_stiffnessx,
            set_desired_force,
            release_force,
            release_compliance_ctrl,
            set_singularity_handling,
            DR_AVOID,
            DR_FC_MOD_ABS,
        )

        from DR_common2 import posj

        # 명령어 모음
        self.movej = movej
        self.wait = wait
        self.set_digital_output = set_digital_output
        self.task_compliance_ctrl = task_compliance_ctrl
        self.set_stiffnessx = set_stiffnessx
        self.set_desired_force = set_desired_force
        self.release_force = release_force
        self.release_compliance_ctrl = release_compliance_ctrl
        self.set_singularity_handling = set_singularity_handling

        self.DR_AVOID = DR_AVOID
        self.DR_FC_MOD_ABS = DR_FC_MOD_ABS

        # 변수 모음
        self.home = posj(0, 0, 50, 0, 90, 0)

        self.lidpoint = [
            posj(2.31, 18.53, 22.84, -11.57, 87.51, 0.00),  # 뚜껑 닫을 위치 위
            posj(2.31, 24.80, 26.88, -11.58, 87.82, 0.00),  # 뚜껑 닫을 위치
            posj(2.48, 24.24, 28.54, -12.24, 99.42, 0.00),  # 뚜껑 닫기
        ]

        self.movejpoint = [
            posj(5.58, 31.66, 27.65, -13.56, 92.88, 0.00),  # 래버 누르기 전
            posj(5.58, 31.66, 20.56, -13.56, 92.88, 0.00),  # 래버 누름
        ]

    # 함수 모음
    def gripper_close(self):
        self.node.get_logger().info("그리퍼 닫기 실행")
        self.set_digital_output(1, 1)
        self.set_digital_output(2, 0)

    def go_home(self):
        self.movej(self.home, vel=30, acc=30)

    # 뚜껑 닫기
    def close_lid(self):
        self.node.get_logger().info("close_lid 실행")

        # 뚜껑 닫을 위치 위로 이동
        self.movej(self.lidpoint[0], vel=30, acc=30)

        # 뚜껑 닫을 위치로 내려오기
        self.movej(self.lidpoint[1], vel=20, acc=20)

        # 뚜껑 닫기
        self.movej(self.lidpoint[2], vel=20, acc=20)

        self.node.get_logger().info("close_lid 완료")

    # 래버 누르고 떼기
    def press_lever(self):
        self.node.get_logger().info("press_lever 실행")

        # 래버 앞으로 이동
        self.movej(self.movejpoint[0], vel=30, acc=30)

        # 힘 제어로 누르기
        self.task_compliance_ctrl()

        self.set_stiffnessx(
            [3000, 3000, 3000, 200, 200, 200],
            time=0.0
        )

        self.set_desired_force(
            [0, 0, -40, 0, 0, 0],
            [0, 0, 1, 0, 0, 0],
            time=0.0,
            mod=self.DR_FC_MOD_ABS
        )

        self.wait(3.0)

        # 힘 제어 끄기 (래버에서 떼기)
        self.release_force(time=0.0)
        self.release_compliance_ctrl()

        self.movej(self.movejpoint[0], vel=20, acc=20)

        self.node.get_logger().info("press_lever 완료")

    # 매니저가 호출하는 함수
    def run(self):
        self.node.get_logger().info("Finish 실행")

        #self.set_singularity_handling(self.DR_AVOID)

        # 집으로 가서 그리퍼 닫기 (그리퍼 클로즈 시 유지)
        self.go_home()
        self.gripper_close()
        self.wait(1.0)

        self.close_lid()
        self.press_lever()
        self.go_home()

        self.node.get_logger().info("Finish 완료")

# 이 파일만 단독으로 테스트할 때 사용
def main(args=None):
    rclpy.init(args=args)
    node = rclpy.create_node("finish", namespace=ROBOT_ID)
    DR_init.__dsr__node = node

    try:
        finish = Finish(node)
        finish.run()

    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()