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

        # 변기 위에 세제 들고 있을 posj값
        self.bleach_home = posj(0.0, 0.0, 51.5, 0.0, 90.0, 93.3)
        # 변기 좌표 4개(세제 돌릴 위치)
        self.bleach_start = posx(427.60, -7.93, 505.72, 40.41, -171.26, 135.89)
        self.bleach_via1 = posx(384.86, 30.47, 505.72, 37.27, -166.55, 126.64)
        self.bleach_half = posx(338.66, -0.33, 505.72, 38.02, -161.64, 131.44)
        self.bleach_via2 = posx(415.89, -38.78, 505.72, 38.53, -161.64, 137.57)

    # 그리퍼 열기
    def gripper_open(self):
        set_digital_output(1, 0)
        set_digital_output(2, 1)

    # 그리퍼 닫기
    def gripper_close(self):
        set_digital_output(1, 1)
        set_digital_output(2, 0)

    # 세제 홈위치로 이동
    def go_home(self):
        movej(self.bleach_home, vel=self.vel, acc=self.acc)

    # 세제 도포 시작부분으로 이동
    def move_to_start(self):
        movel(self.bleach_start, vel=self.vel, acc=self.acc)

    # 세제 도포
    def apply(self):
        self.move_to_start()
        # 왼쪽 반원 돌리기
        movec(self.bleach_via1, self.bleach_half, vel=self.vel, acc=self.acc)
        # 오른쪽 반원 돌리기 (시작점 복귀)
        movec(self.bleach_via2, self.bleach_start, vel=self.vel, acc=self.acc)
        return True


def main(args=None):
    rclpy.init(args=args)
    node = rclpy.create_node("apply_bleach", namespace=ROBOT_ID)
    DR_init.__dsr__node = node
    
    global set_tool, set_tcp, movej, movel, movesj, movec
    global set_digital_output, wait, get_current_posx, trans
    global task_compliance_ctrl, set_stiffnessx, set_desired_force
    global release_force, release_compliance_ctrl, amove_periodic
    global set_singularity_handling, check_force_condition
    global DR_BASE, DR_AVOID, DR_FC_MOD_ABS, DR_AXIS_Z
    global posx, posj

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

    try:
        bleach = ApplyBleach(node)
        bleach.go_home()
        bleach.apply()
        bleach.go_home()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()