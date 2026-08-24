"""Brush Clean: picks up a brush and scrubs the toilet bowl."""

import math

import DR_init


class BrushClean:
    def __init__(self, node, vel=30, acc=30):
        self.node = node

        self.vel = vel
        self.acc = acc
        # =====================================================
        # 0. HOME POSE
        # =====================================================
        self.home_posj_1 = 0.0
        self.home_posj_2 = 0.0
        self.home_posj_3 = 50.0
        self.home_posj_4 = 0.0  
        self.home_posj_5 = 90.0
        self.home_posj_6 = 0.0  


        # =====================================================
        # 1. BRUSH PICK / PLACE
        # =====================================================
        #
        # 실제 Teaching 값
        #
        # 브러시를 잡는 위치 = 다시 내려놓는 위치
        #

        self.brush_pick_x = 479.05
        self.brush_pick_y = 205.83
        self.brush_pick_z = 417.96

        self.brush_pick_rx = 29.86
        self.brush_pick_ry = 174.92
        self.brush_pick_rz = -47.68

        # 브러시 위에서 접근할 거리
        self.brush_approach_height = 100.0

        # =====================================================
        # 2. TOILET CLEAN CENTER
        # =====================================================
        #
        # 브러시를 변기 중앙에 넣었을 때
        # 실제 Teaching 값
        #
        # 여기서 브러시 아래쪽도 살짝 닿음.
        #

        self.center_x = 452.88
        self.center_y = -76.37

        # 중요:
        # 청소 중 Z는 이 값으로 고정
        self.clean_z = 474.32

        # 중요:
        # 브러시는 360도이므로
        # orientation은 청소 중 계속 고정
        self.clean_rx = 173.65
        self.clean_ry = -173.82
        self.clean_rz = -176.06

        # =====================================================
        # 3. ACTUAL WALL LIMITS
        # =====================================================
        #
        # 실제로 브러시가 네 면 벽에 닿았을 때 측정한 좌표
        #
        # Z값은 사용하지 않음.
        # X/Y 경계값만 사용.
        #

        # X- 방향 벽
        self.x_min = 390.79

        # X+ 방향 벽
        self.x_max = 522.09

        # Y- 방향 벽
        self.y_min = -130.70

        # Y+ 방향 벽
        self.y_max = -45.55

        # =====================================================
        # 4. DISTANCE FROM CENTER TO EACH WALL
        # =====================================================
        #
        # 중심이 정확히 기하학적 중앙일 필요가 없으므로
        # 각 방향 반경을 따로 계산.
        #

        # 452.88 - 390.79 = 62.09 mm
        self.radius_x_minus = (self.center_x - self.x_min)
        # 452.88 - 390.79 = 62.09 mm

        self.radius_x_plus = (self.x_max - self.center_x)
        # 522.09 - 452.88 = 69.21 mm

        self.radius_y_minus = (self.center_y - self.y_min)
        # -76.37 - (-130.70) = 54.33 mm

        self.radius_y_plus = (self.y_max - self.center_y)
        # -45.55 - (-76.37) = 30.82 mm

        # =====================================================
        # 5. CLEANING PARAMETERS
        # =====================================================

        # 변기 둘레를 몇 도 간격으로 이동할지
        #
        # 15도 -> 24 points
        #
        self.angle_step = 15

        # Periodic scrub
        #
        # ±6 mm
        # 전체 stroke = 12 mm
        self.scrub_amp = 6.0

        self.scrub_period = 1.2
        self.scrub_repeat = 3

        # =====================================================
        # 6. COMPLIANCE
        # =====================================================

        self.compliance_enabled = False

    # =========================================================
    # MOVE TO HOME
    # =========================================================

    def move_to_home(self):
        from DSR_ROBOT2 import (movej, DR_BASE)

        self.node.get_logger().info("========== RESET POSITION: HOME ==========")
        movej(self.get_home_posej(), vel=self.vel, acc=self.acc)


    def get_home_posej(self):
        from DSR_ROBOT2 import posj

        home_posej = posj(
                self.home_posj_1,
                self.home_posj_2,
                self.home_posj_3,
                self.home_posj_4,
                self.home_posj_5,
                self.home_posj_6,
            )

        return home_posej
    
    # =========================================================
    # GRIPPER
    # =========================================================

    def gripper_open(self):
        """
        Gripper OPEN.

        """

        from DSR_ROBOT2 import (set_digital_output, wait)

        self.node.get_logger().info("Gripper OPEN")

        set_digital_output(1, 0)
        set_digital_output(2, 1)

        wait(1.0)

    def gripper_close(self):
        """
        Gripper CLOSE.
        """

        from DSR_ROBOT2 import (set_digital_output, wait)

        self.node.get_logger().info("Gripper CLOSE")

        set_digital_output(1, 1)
        set_digital_output(2, 0)

        wait(1.0)

    # =========================================================
    # BRUSH PICK POSES
    # =========================================================

    def get_brush_pick_pose(self):
        from DSR_ROBOT2 import posx

        self.node.get_logger().info("Get brush pick pose")

        pick_point = posx(
            self.brush_pick_x,
            self.brush_pick_y,
            self.brush_pick_z,
            self.brush_pick_rx,
            self.brush_pick_ry,
            self.brush_pick_rz,
        )

        self.node.get_logger().info(
                    f"pick point: {pick_point}"
                )
        
        return pick_point

    def get_brush_approach_pose(self):
        """
        브러시 잡는 위치 바로 위. 

        X/Y/orientation은 그대로 두고
        BASE Z만 +100 mm.
        """

        from DSR_ROBOT2 import posx, posj

        self.node.get_logger().info("Get brush approach pose")


        brush_approach_posj = posj(
            25.06,
            29.35,
            30.58,
            -2.98,
            118.38,
            -62.38
        )

        approach_point = posx(
            self.brush_pick_x,
            self.brush_pick_y,
            self.brush_pick_z
            + self.brush_approach_height,
            self.brush_pick_rx,
            self.brush_pick_ry,
            self.brush_pick_rz,
        )
        self.node.get_logger().info(
                    f"approach point: {approach_point}"
                )
        
        return approach_point


    def get_brush_approach_posej(self):
        """
        브러시 잡는 위치 바로 위. 

        X/Y/orientation은 그대로 두고
        BASE Z만 +100 mm.
        """

        from DSR_ROBOT2 import posj

        self.node.get_logger().info("Get brush approach pose")


        brush_approach_posj = posj(
            25.06,
            29.35,
            30.58,
            -2.98,
            118.38,
            -62.38
        )


        self.node.get_logger().info(
                    f"approach point: {brush_approach_posj}"
                )
        
        return brush_approach_posj

    # =========================================================
    # PICK BRUSH
    # =========================================================

    def pick_brush(self):
        """
        위에서 아래로 내려가 브러시를 잡는다.

            Approach
                ↓
            Gripper OPEN
                ↓
              Pick
                ↓
            Gripper CLOSE
                ↓
              Lift
        """

        from DSR_ROBOT2 import (movel, movej, wait, DR_BASE, posx, get_current_posx)

        self.move_to_home()

        self.node.get_logger().info("========== PICK BRUSH ==========")

        approach_j = self.get_brush_approach_posej() 
        approach = self.get_brush_approach_pose()
        pick = self.get_brush_pick_pose()

        # -----------------------------------------------------
        # 1. 브러시 위로 이동
        # -----------------------------------------------------

        self.node.get_logger().info("Move above brush")


        movej(
            approach_j,
            vel=self.vel,
            acc=self.acc,
        )


        ##################################

        position, sol = get_current_posx(ref=DR_BASE)

        self.node.get_logger().info(f"Current position: {position}, sol={sol}")

        move_point = posx(
            position[0],
            position[1],
            position[2] - 70.0,
            position[3],
            position[4],
            position[5],
        )

        movel(move_point, vel=self.vel, acc=self.acc)

        ###############################


        # movel(
        #     approach,
        #     vel=self.vel,
        #     acc=self.acc,
        #     ref=DR_BASE,
        # )

        # -----------------------------------------------------
        # 2. Gripper open
        # -----------------------------------------------------

        self.gripper_open()

        # -----------------------------------------------------
        # 3. 위 -> 아래
        # -----------------------------------------------------

        self.node.get_logger().info("Move down to brush")

        movel(
            pick,
            vel=30,
            acc=30,
            ref=DR_BASE,
        )

        wait(1.0)

        # -----------------------------------------------------
        # 4. Brush 잡기
        # -----------------------------------------------------

        self.gripper_close()

        wait(1.0)

        # -----------------------------------------------------
        # 5. 수직으로 올리기
        # -----------------------------------------------------

        self.node.get_logger().info("Lift brush")

        movel(
            approach,
            vel=self.vel,
            acc=self.acc,
            ref=DR_BASE,
        )

        self.node.get_logger().info("Brush picked")

    # =========================================================
    # PLACE BRUSH
    # =========================================================

    def place_brush(self):
        """
        청소 후 원래 위치로 브러시를 돌려놓는다.

        위에서 아래로 내려놓음.
        """

        from DSR_ROBOT2 import (
            movel, movej,
            wait,
            DR_BASE,
            get_current_posx
        )

        self.move_to_home()

        self.node.get_logger().info("========== PLACE BRUSH ==========")

        approach = self.get_brush_approach_pose()

        approach_j = self.get_brush_approach_posej()


        ##################################

        position, sol = get_current_posx(ref=DR_BASE)

        self.node.get_logger().info(f"Current position: {position}, sol={sol}")

        move_point = [
            position[0],
            position[1],
            position[2] - 70.0,
            position[3],
            position[4],
            position[5],
        ]


        ###############################

        pickup = self.get_brush_pick_pose()

        place = self.get_brush_pick_pose()

        # -----------------------------------------------------
        # 1. 보관 위치 위
        # -----------------------------------------------------

        # movel(
        #     approach,
        #     vel=self.vel,
        #     acc=self.acc,
        #     ref=DR_BASE,
        # )

        movej(
            approach_j,
            vel=self.vel,
            acc=self.acc,)

        # -----------------------------------------------------
        # 2. 위 -> 아래
        # -----------------------------------------------------

        movel(
            pickup,
            vel=self.vel,
            acc=self.acc,
            ref=DR_BASE,
        )

        wait(1.0)

        # -----------------------------------------------------
        # 3. 놓기
        # -----------------------------------------------------

        self.gripper_open()

        wait(1.0)

        # -----------------------------------------------------
        # 4. 그리퍼만 수직 상승
        # -----------------------------------------------------

        movel(
            approach,
            vel=self.vel,
            acc=self.acc,
            ref=DR_BASE,
        )

        self.node.get_logger().info("Brush returned")

    # =========================================================
    # CLEAN CENTER
    # =========================================================

    def get_clean_center_posej(self):
        from DSR_ROBOT2 import posj

        center_posej = posj(
            self.home_posj_1,
            self.home_posj_2,
            self.home_posj_3,
            self.home_posj_4,
            self.home_posj_5,
            self.home_posj_6,
        )

        return center_posej

    # =========================================================
    # CLEAN CENTER
    # =========================================================

    def get_clean_center_pose(self):
        from DSR_ROBOT2 import posx

        center_pose = posx(
            self.center_x,
            self.center_y,
            self.clean_z,
            self.clean_rx,
            self.clean_ry,
            self.clean_rz,
        )
        return center_pose

    # =========================================================
    # CLEAN ABOVE CENTER
    # =========================================================

    def get_clean_above_pose(self):
        """
        변기에서 솔을 넣고/뺄 때 사용하는 안전 위치.

        중앙 기준 Z + 100 mm.
        """

        from DSR_ROBOT2 import posx

        return posx(
            self.center_x,
            self.center_y,
            self.clean_z + 100.0,
            self.clean_rx,
            self.clean_ry,
            self.clean_rz,
        )

    # =========================================================
    # REAL-WALL-BASED PATH
    # =========================================================

    def get_cleaning_xy(self, angle_deg):
        """
        실제 네 면 측정값을 이용하여 XY 경로 생성.

        중심에서 각 방향까지의 거리가 서로 다르므로
        +X / -X / +Y / -Y 반경을 따로 사용한다.
        """

        theta = math.radians(angle_deg)

        cos_t = math.cos(theta)
        sin_t = math.sin(theta)

        # -----------------------------------------------------
        # X radius
        # -----------------------------------------------------

        if cos_t >= 0:
            radius_x = self.radius_x_plus
        else:
            radius_x = self.radius_x_minus

        # -----------------------------------------------------
        # Y radius
        # -----------------------------------------------------

        if sin_t >= 0:
            radius_y = self.radius_y_plus
        else:
            radius_y = self.radius_y_minus

        x = (
            self.center_x
            + radius_x * cos_t
        )

        y = (
            self.center_y
            + radius_y * sin_t
        )

        return x, y

    # =========================================================
    # NUMERICAL TANGENT
    # =========================================================

    def get_tangent(self, angle_deg):
        """
        현재 경로의 tangent를 수치적으로 계산한다.

        P(theta + dtheta) - P(theta - dtheta)

        실제 네 면 좌표를 기반으로 만든 비대칭 경로이므로
        단순 타원 공식보다 이 방식이 편하다.
        """

        delta = 1.0

        x1, y1 = self.get_cleaning_xy(angle_deg - delta)

        x2, y2 = self.get_cleaning_xy(angle_deg + delta)

        tx = x2 - x1
        ty = y2 - y1

        length = math.sqrt(tx * tx + ty * ty)

        if length < 1e-6:
            raise ValueError(
                "Cannot calculate tangent."
            )

        tx /= length
        ty /= length

        return tx, ty

    # =========================================================
    # COMPLIANCE ON
    # =========================================================

    def enable_compliance(self):
        """
        XY 방향에 compliance를 줘서
        실제 벽과 경로 오차를 흡수한다.

        Z는 비교적 높은 stiffness 유지.
        """

        from DSR_ROBOT2 import (
            task_compliance_ctrl,
        )

        self.node.get_logger().info(
            "Compliance ON"
        )

        task_compliance_ctrl(
            stx=[
                500.0,    # X
                500.0,    # Y
                3000.0,   # Z
                200.0,    # RX
                200.0,    # RY
                200.0,    # RZ
            ],
            time=0.5,
        )

        self.compliance_enabled = True

    # =========================================================
    # COMPLIANCE OFF
    # =========================================================

    def disable_compliance(self):
        from DSR_ROBOT2 import (
            release_compliance_ctrl,
        )

        if not self.compliance_enabled:
            return

        self.node.get_logger().info(
            "Compliance OFF"
        )

        release_compliance_ctrl()

        self.compliance_enabled = False

    # =========================================================
    # PERIODIC SCRUB
    # =========================================================

    def scrub(self, angle_deg):
        """
        현재 벽의 tangent 방향으로 쓱싹.

        Z와 orientation은 바뀌지 않는다.
        """

        from DSR_ROBOT2 import (
            move_periodic,
            DR_BASE,
        )

        tx, ty = self.get_tangent(
            angle_deg
        )

        amp_x = (
            self.scrub_amp * tx
        )

        amp_y = (
            self.scrub_amp * ty
        )

        self.node.get_logger().info(
            f"Scrub | "
            f"amp_x={amp_x:.2f} mm, "
            f"amp_y={amp_y:.2f} mm"
        )

        move_periodic(
            amp=[
                amp_x,
                amp_y,
                0.0,
                0.0,
                0.0,
                0.0,
            ],
            period=self.scrub_period,
            atime=0.3,
            repeat=self.scrub_repeat,
            ref=DR_BASE,
        )

    # =========================================================
    # CLEAN BOWL
    # =========================================================

    def clean_bowl(self):
        """
        실제 변기 청소.

        1. 변기 중앙 위로 이동
        2. 중앙으로 수직 진입
        3. 첫 wall point로 이동
        4. Compliance ON
        5. 둘레 이동 + periodic scrub
        6. Compliance OFF
        7. 중앙 복귀
        8. 위로 수직 탈출
        """

        from DSR_ROBOT2 import (
            posx,
            movel,
            wait,
            DR_BASE,
        )

        # -----------------------------------------------------
        # 1. 변기 중앙 위
        # -----------------------------------------------------

        above = self.get_clean_above_pose()
        center = self.get_clean_center_pose()

        self.node.get_logger().info(
            "Move above toilet center"
        )

        movel(
            above,
            vel=15,
            acc=15,
            ref=DR_BASE,
        )

        # -----------------------------------------------------
        # 2. 중앙으로 내려가기
        # -----------------------------------------------------

        self.node.get_logger().info(
            "Insert brush into toilet"
        )

        movel(
            center,
            vel=8,
            acc=8,
            ref=DR_BASE,
        )

        wait(0.3)

        # -----------------------------------------------------
        # 3. Cleaning angles
        # -----------------------------------------------------

        angles = list(
            range(
                0,
                360,
                self.angle_step,
            )
        )

        # -----------------------------------------------------
        # 4. 첫 wall 위치로 이동
        # -----------------------------------------------------

        first_angle = angles[0]

        x, y = self.get_cleaning_xy(
            first_angle
        )

        first_target = posx(
            x,
            y,
            self.clean_z,
            self.clean_rx,
            self.clean_ry,
            self.clean_rz,
        )

        self.node.get_logger().info(
            "Move to first wall"
        )

        movel(
            first_target,
            vel=6,
            acc=6,
            ref=DR_BASE,
        )

        # -----------------------------------------------------
        # 5. Compliance ON
        # -----------------------------------------------------

        self.enable_compliance()

        # -----------------------------------------------------
        # 6. Clean all wall sections
        # -----------------------------------------------------

        for i, angle in enumerate(angles):

            self.node.get_logger().info(
                "--------------------------------"
            )

            self.node.get_logger().info(
                f"Cleaning "
                f"{i + 1}/{len(angles)} "
                f"| angle={angle}"
            )

            x, y = self.get_cleaning_xy(
                angle
            )

            target = posx(
                x,
                y,

                # Z 항상 고정
                self.clean_z,

                # Orientation 항상 고정
                self.clean_rx,
                self.clean_ry,
                self.clean_rz,
            )

            # ---------------------------------------------
            # 다음 벽 구간
            # ---------------------------------------------

            if i > 0:
                movel(
                    target,
                    vel=5,
                    acc=5,
                    ref=DR_BASE,
                )

            # ---------------------------------------------
            # 쓱싹
            # ---------------------------------------------

            self.scrub(
                angle
            )

            wait(0.15)

        # -----------------------------------------------------
        # 7. Compliance OFF
        # -----------------------------------------------------

        self.disable_compliance()

        # -----------------------------------------------------
        # 8. 중앙으로 돌아오기
        # -----------------------------------------------------

        self.node.get_logger().info(
            "Return to toilet center"
        )

        movel(
            center,
            vel=6,
            acc=6,
            ref=DR_BASE,
        )

        # -----------------------------------------------------
        # 9. 수직으로 위로 빼기
        # -----------------------------------------------------

        self.node.get_logger().info(
            "Lift brush out of toilet"
        )

        movel(
            above,
            vel=8,
            acc=8,
            ref=DR_BASE,
        )

    # =========================================================
    # MAIN
    # =========================================================

    def run(self):
        """
        Full sequence:

        Pick brush
            ↓
        Move above toilet
            ↓
        Insert vertically
            ↓
        Clean
            ↓
        Return center
            ↓
        Lift vertically
            ↓
        Place brush
        """

        self.node.get_logger().info("========== BRUSH CLEAN START ==========")

        try:
            # -------------------------------------------------
            # 1. Brush pickup
            # -------------------------------------------------

            self.pick_brush()


            # -------------------------------------------------
            # 2. Clean toilet
            # -------------------------------------------------

            #self.clean_bowl()

            # -------------------------------------------------
            # 3. Return brush
            # -------------------------------------------------

            self.place_brush()

            self.node.get_logger().info("========== BRUSH CLEAN COMPLETE ==========")

            return True

        except Exception as e:

            self.node.get_logger().error(
                f"Brush cleaning failed: "
                f"{type(e).__name__}: {e}"
            )

            return False

        finally:
            # -------------------------------------------------
            # 에러가 나더라도 compliance 해제
            # -------------------------------------------------

            if self.compliance_enabled:

                try:
                    self.disable_compliance()

                except Exception as e:

                    self.node.get_logger().error(
                        "Failed to release compliance: "
                        f"{e}"
                    )


# =============================================================
# STANDALONE TEST
# =============================================================

def main(args=None):
    import rclpy

    ROBOT_ID = "dsr01"
    ROBOT_MODEL = "m0609"

    rclpy.init(args=args)

    node = rclpy.create_node("brush_clean", namespace=ROBOT_ID)

    DR_init.__dsr__id = ROBOT_ID
    DR_init.__dsr__model = ROBOT_MODEL
    DR_init.__dsr__node = node

    try:
        cleaner = BrushClean(node)

        cleaner.run()

    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()