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

        self.home_posj_1 = -8.0
        self.home_posj_2 = -19.0
        self.home_posj_3 = 66.5
        self.home_posj_4 = 0.0
        self.home_posj_5 = 90.0
        self.home_posj_6 = 0.0

        # =====================================================
        # 1. BRUSH PICK / PLACE
        # =====================================================
        #
        # 기존 값 그대로
        #

        self.brush_pick_x = 479.05
        self.brush_pick_y = 205.83
        self.brush_pick_z = 417.96

        self.brush_pick_rx = 29.86
        self.brush_pick_ry = 174.92
        self.brush_pick_rz = -47.68

        self.brush_approach_height = 100.0

        # =====================================================
        # 2. CLEAN ABOVE
        # =====================================================

        self.clean_above_x = 483.47
        self.clean_above_y = -50.60
        self.clean_above_z = 411.46

        self.clean_above_rx = 129.41
        self.clean_above_ry = -166.45
        self.clean_above_rz = 61.73

        # =====================================================
        # 3. CENTER
        # =====================================================
        #
        # 첫 번째 사진 center
        #

        self.center_x = 494.68
        self.center_y = -76.03
        self.center_z = 268.77

        # =====================================================
        # 4. CLEANING ORIENTATION
        # =====================================================
        #
        # 브러시 수직 고정
        #

        self.clean_rx = 173.65
        self.clean_ry = -173.82
        self.clean_rz = -176.06

        # =====================================================
        # 5. WALL POINTS
        # =====================================================
        #
        # 실제 닦는 순서대로 P1 -> P8
        #
        #              P1
        #
        #       P8            P2
        #
        #   P7                    P3
        #
        #       P6            P4
        #
        #              P5
        #

        self.wall_points = [

            # P1
            [497.20, -17.26, 273.15],

            # P2
            [547.70, -33.13, 272.87],

            # P3
            [558.64, -84.99, 273.67],

            # P4
            [550.65, -113.86, 274.78],

            # P5
            [491.32, -125.84, 274.43],

            # P6
            [442.78, -118.35, 274.27],

            # P7
            [411.79, -82.39, 276.25],

            # P8
            [427.66, -38.67, 275.68],
        ]

        # =====================================================
        # 6. SAFETY Z OFFSET
        # =====================================================
        #
        #
        # 기존 좌표가 너무 낮아서
        # 솔이 변기 바닥에 박힘.
        #
        # 모든 청소 위치의 Z를 20 mm 올린다.
        #
        # 바닥에 아직 닿으면:
        #
        # 20 -> 25 -> 30
        #
        # 너무 높으면:
        #
        # 20 -> 15 -> 10
        #

        self.z_safety_offset = 0.0

        # =====================================================
        # 7. CLEANING SPEED
        # =====================================================
        self.clean_vel = 10.0
        self.clean_acc = 10.0

        # =====================================================
        # 8. SCRUB
        # =====================================================
        #
        # 지금은 OFF.
        #
        # 먼저 바닥에 안 박히는지 확인 후:
        #
        # self.scrub_angle = 3.0
        #

        self.scrub_angle = 0.0

        self.scrub_points_per_segment = 10

        # =====================================================
        # 9. WALL FORCE
        # =====================================================
        #
        # 지금은 OFF.
        #
        # 경로 확인 후:
        #
        # 1.0 -> 2.0 -> 3.0
        #

        self.wall_force = 0.0

        # =====================================================
        # 10. COMPLIANCE
        # =====================================================

        self.compliance_enabled = False

    # =========================================================
    # MOVE TO HOME
    # =========================================================

    def move_to_home(self):

        from DSR_ROBOT2 import movej

        self.node.get_logger().info(
            "========== RESET POSITION: HOME =========="
        )

        movej(
            self.get_home_posej(),
            vel=self.vel,
            acc=self.acc,
        )

    def get_home_posej(self):

        from DSR_ROBOT2 import posj

        return posj(
            self.home_posj_1,
            self.home_posj_2,
            self.home_posj_3,
            self.home_posj_4,
            self.home_posj_5,
            self.home_posj_6,
        )

    # =========================================================
    # GRIPPER
    # =========================================================

    def gripper_open(self):

        from DSR_ROBOT2 import (
            set_digital_output,
            wait,
        )

        self.node.get_logger().info(
            "Gripper OPEN"
        )

        set_digital_output(1, 0)
        set_digital_output(2, 1)

        wait(0.3)

    def gripper_close(self):

        from DSR_ROBOT2 import (
            set_digital_output,
            wait,
        )

        self.node.get_logger().info(
            "Gripper CLOSE"
        )

        set_digital_output(1, 1)
        set_digital_output(2, 0)

        wait(0.3)

    # =========================================================
    # BRUSH PICK POSES
    # =========================================================

    def get_brush_pick_pose(self):

        from DSR_ROBOT2 import posx

        self.node.get_logger().info(
            "Get brush pick pose"
        )

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

        from DSR_ROBOT2 import posx

        self.node.get_logger().info(
            "Get brush approach pose"
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

        from DSR_ROBOT2 import posj

        self.node.get_logger().info(
            "Get brush approach posej"
        )

        brush_approach_posj = posj(
            26.0,
            25.0,
            45.0,
            -2.5,
            107.0,
            -54.0,
        )

        self.node.get_logger().info(
            f"approach point: {brush_approach_posj}"
        )

        return brush_approach_posj

    def get_brush_pick_posej(self):

        from DSR_ROBOT2 import posj

        self.node.get_logger().info(
            "Get brush pick posej"
        )

        brush_pick_posj = posj(
            27.0,
            29.0,
            54.0,
            -5.0,
            100.0,
            -54.0,
        )

        self.node.get_logger().info(
            f"pick point: {brush_pick_posj}"
        )

        return brush_pick_posj

    # =========================================================
    # PICK BRUSH
    # =========================================================
    #
    # 기존 코드 그대로
    #

    def pick_brush(self):

        from DSR_ROBOT2 import (
            movel,
            movej,
            wait,
            DR_BASE,
            posx,
            get_current_posx,
        )

        self.move_to_home()

        self.node.get_logger().info(
            "========== PICK BRUSH =========="
        )

        approach_j = self.get_brush_approach_posej()
        pick_j = self.get_brush_pick_posej()

        self.node.get_logger().info(
            "Move above brush"
        )

        movej(
            approach_j,
            vel=10.0,
            acc=10.0,
        )

        self.gripper_open()

        wait(0.5)

        self.node.get_logger().info(
            "Move down to brush"
        )

        movej(
            pick_j,
            vel=self.vel,
            acc=self.acc,
        )

        wait(0.5)

        self.gripper_close()

        wait(0.5)

        self.node.get_logger().info(
            "Lift brush"
        )

        movej(
            approach_j,
            vel=self.vel,
            acc=self.acc,
        )

        self.node.get_logger().info(
            "Brush picked"
        )

        self.move_to_home()

    # =========================================================
    # PLACE BRUSH
    # =========================================================
    #
    # 기존 코드 그대로
    #

    def place_brush(self):

        from DSR_ROBOT2 import (
            movel,
            movej,
            wait,
            DR_BASE,
            get_current_posx,
        )

        self.move_to_home()

        self.node.get_logger().info(
            "========== PLACE BRUSH =========="
        )

        approach_j = self.get_brush_approach_posej()
        pick_j = self.get_brush_pick_posej()

        movej(
            approach_j,
            vel=self.vel,
            acc=self.acc,
        )

        wait(0.5)

        movej(
            pick_j,
            vel=self.vel,
            acc=self.acc,
        )

        wait(0.5)

        self.gripper_open()

        wait(0.5)

        movej(
            approach_j,
            vel=self.vel,
            acc=self.acc,
        )

        self.node.get_logger().info(
            "Brush returned"
        )

        self.move_to_home()

    # =========================================================
    # CLEAN ABOVE
    # =========================================================

    def get_clean_above_pose(self):

        from DSR_ROBOT2 import posx

        return posx(
            self.clean_above_x,
            self.clean_above_y,
            self.clean_above_z,
            self.clean_above_rx,
            self.clean_above_ry,
            self.clean_above_rz,
        )

    # =========================================================
    # CLEAN CENTER
    # =========================================================

    def get_clean_center_pose(self):

        from DSR_ROBOT2 import posx

        safe_z = (
            self.center_z
            + self.z_safety_offset
        )

        self.node.get_logger().info(
            f"Safe CENTER Z = {safe_z:.2f}"
        )

        return posx(
            self.center_x,
            self.center_y,
            safe_z,
            self.clean_rx,
            self.clean_ry,
            self.clean_rz,
        )

    # =========================================================
    # SAFE WALL POINT
    # =========================================================

    def get_safe_wall_point(self, point):
        """
        현재 wall teaching point의
        X/Y는 그대로 사용하고,
        Z만 safety offset 만큼 올린다.
        """

        return [
            point[0],
            point[1],
            point[2]
            + self.z_safety_offset,
        ]

    # =========================================================
    # GET WALL POSE
    # =========================================================

    def get_wall_pose(self, point):

        from DSR_ROBOT2 import posx

        safe_point = (
            self.get_safe_wall_point(
                point
            )
        )

        return posx(
            safe_point[0],
            safe_point[1],
            safe_point[2],
            self.clean_rx,
            self.clean_ry,
            self.clean_rz,
        )

    # =========================================================
    # COMPLIANCE ON
    # =========================================================

    def enable_compliance(self):

        from DSR_ROBOT2 import (
            task_compliance_ctrl,
            set_ref_coord,
            DR_BASE,
        )

        self.node.get_logger().info(
            "Compliance ON"
        )

        # compliance 들어가기 전에 딱 한 번
        set_ref_coord(DR_BASE)

        task_compliance_ctrl(
            stx=[
                500.0,
                500.0,
                3000.0,
                200.0,
                200.0,
                200.0,
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
    # WALL NORMAL
    # =========================================================

    def calculate_wall_normal(
        self,
        p1,
        p2
    ):

        dx = (
            p2[0] -
            p1[0]
        )

        dy = (
            p2[1] -
            p1[1]
        )

        length = math.sqrt(
            dx * dx +
            dy * dy
        )

        if length < 1e-6:

            raise ValueError(
                "Wall points are too close."
            )

        tx = dx / length
        ty = dy / length

        nx = -ty
        ny = tx

        mid_x = (
            p1[0] +
            p2[0]
        ) / 2.0

        mid_y = (
            p1[1] +
            p2[1]
        ) / 2.0

        vx = (
            mid_x -
            self.center_x
        )

        vy = (
            mid_y -
            self.center_y
        )

        dot = (
            nx * vx +
            ny * vy
        )

        if dot < 0:

            nx = -nx
            ny = -ny

        return nx, ny

    # =========================================================
    # WALL FORCE
    # =========================================================

    def apply_wall_force(self, p1, p2):

        if self.wall_force <= 0.0:
            return

        from DSR_ROBOT2 import (
            set_desired_force,
            DR_FC_MOD_REL,
        )

        nx, ny = self.calculate_wall_normal(
            p1,
            p2
        )

        fx = nx * self.wall_force
        fy = ny * self.wall_force

        self.node.get_logger().info(
            f"Wall Force | "
            f"Fx={fx:.2f} N | "
            f"Fy={fy:.2f} N"
        )


        set_desired_force(
            fd=[
                fx,
                fy,
                0.0,
                0.0,
                0.0,
                0.0,
            ],
            dir=[
                1,
                1,
                0,
                0,
                0,
                0,
            ],
            time=0.3,
            mod=DR_FC_MOD_REL,
        )

    # =========================================================
    # CREATE SCRUB SEGMENT
    # =========================================================

    def make_scrub_segment(
        self,
        p1,
        p2
    ):
        """
        P1 -> P2 사이를 이동.

        X/Y:
            wall path 따라 이동.

        Z:
            teaching Z
            + safety offset.

        Rz:
            scrub_angle이 0이면 고정.

            나중에 3.0 정도로 설정하면
            +/- 회전 scrub.
        """

        from DSR_ROBOT2 import posx

        points = []

        count = (
            self.scrub_points_per_segment
        )

        for i in range(
            1,
            count + 1
        ):

            t = (
                i /
                count
            )

            # -------------------------------------------------
            # X
            # -------------------------------------------------

            x = (
                p1[0]
                + (p2[0] - p1[0])
                * t
            )

            # -------------------------------------------------
            # Y
            # -------------------------------------------------

            y = (
                p1[1]
                + (p2[1] - p1[1])
                * t
            )

            # -------------------------------------------------
            # Z
            #
            # 핵심:
            # original Z + safety offset
            # -------------------------------------------------

            original_z = (
                p1[2]
                + (p2[2] - p1[2])
                * t
            )

            z = (
                original_z
                + self.z_safety_offset
            )

            # -------------------------------------------------
            # Rz scrub
            # -------------------------------------------------

            if self.scrub_angle > 0.0:

                if i % 2 == 0:

                    rotation = (
                        self.scrub_angle
                    )

                else:

                    rotation = (
                        -self.scrub_angle
                    )

            else:

                rotation = 0.0

            rz = (
                self.clean_rz
                + rotation
            )

            target = posx(
                x,
                y,
                z,
                self.clean_rx,
                self.clean_ry,
                rz,
            )

            points.append(
                target
            )

        return points

    # =========================================================
    # CLEAN ONE SEGMENT
    # =========================================================

    def clean_wall_segment(
        self,
        p1,
        p2,
        segment_number
    ):

        from DSR_ROBOT2 import (
            movesx,
            DR_BASE,
        )

        self.node.get_logger().info(
            "--------------------------------"
        )

        self.node.get_logger().info(
            f"CLEAN SEGMENT "
            f"{segment_number}"
        )

        # -----------------------------------------------------
        # Force
        # -----------------------------------------------------

        self.apply_wall_force(
            p1,
            p2
        )

        # -----------------------------------------------------
        # Safe cleaning path
        # -----------------------------------------------------

        scrub_path = (
            self.make_scrub_segment(
                p1,
                p2
            )
        )

        movesx(
            scrub_path,

            vel=[
                self.clean_vel,
                10.0,
            ],

            acc=[
                self.clean_acc,
                20.0,
            ],

            ref=DR_BASE,
        )

    # =========================================================
    # CLEAN BOWL
    # =========================================================

    def clean_bowl(self):

        from DSR_ROBOT2 import (
            movel,
            wait,
            release_force,
            DR_BASE,
        )

        self.node.get_logger().info(
            "========== CLEAN BOWL =========="
        )

        above = (
            self.get_clean_above_pose()
        )

        center = (
            self.get_clean_center_pose()
        )

        # =====================================================
        # 1. ABOVE
        # =====================================================

        self.node.get_logger().info(
            "Move above toilet"
        )

        movel(
            above,
            vel=15,
            acc=15,
            ref=DR_BASE,
        )

        # =====================================================
        # 2. SAFE CENTER
        # =====================================================

        self.node.get_logger().info(
            "Move to SAFE toilet center"
        )

        movel(
            center,
            vel=self.clean_vel,
            acc=self.clean_acc,
            ref=DR_BASE,
        )

        wait(0.5)

        # =====================================================
        # 3. SAFE P1
        # =====================================================

        p1 = (
            self.wall_points[0]
        )

        p1_pose = (
            self.get_wall_pose(
                p1
            )
        )

        self.node.get_logger().info(
            "Move SAFE center -> SAFE P1"
        )

        movel(
            p1_pose,
            vel=self.clean_vel,
            acc=self.clean_acc,
            ref=DR_BASE,
        )

        wait(0.5)

        # =====================================================
        # 4. COMPLIANCE
        # =====================================================
        #
        # force=0이면 compliance도 처음에는
        # 굳이 켜지 않아도 됨.
        #

        use_force_control = (
            self.wall_force > 0.0
        )

        if use_force_control:

            self.enable_compliance()

        try:

            number_of_points = (
                len(
                    self.wall_points
                )
            )

            # =================================================
            # 5. CLEAN FULL WALL
            # =================================================

            for i in range(
                number_of_points
            ):

                current_point = (
                    self.wall_points[i]
                )

                next_point = (
                    self.wall_points[
                        (i + 1)
                        % number_of_points
                    ]
                )

                self.clean_wall_segment(
                    current_point,
                    next_point,
                    i + 1
                )

            # =================================================
            # 6. FORCE OFF
            # =================================================

            if use_force_control:

                release_force()

                wait(0.3)

        finally:

            if use_force_control:

                try:

                    release_force()

                except Exception:

                    pass

                self.disable_compliance()

        # =====================================================
        # 7. RETURN SAFE CENTER
        # =====================================================

        self.node.get_logger().info(
            "Return to SAFE center"
        )

        movel(
            center,
            vel=self.clean_vel,
            acc=self.clean_acc,
            ref=DR_BASE,
        )

        # =====================================================
        # 8. LIFT OUT
        # =====================================================

        self.node.get_logger().info(
            "Lift brush out"
        )

        movel(
            above,
            vel=10,
            acc=10,
            ref=DR_BASE,
        )

    # =========================================================
    # MAIN
    # =========================================================

    def run(self):

        self.node.get_logger().info(
            "========== BRUSH CLEAN START =========="
        )

        try:

            # =================================================
            # 1. PICK BRUSH
            # =================================================

            self.pick_brush()

            # =================================================
            # 2. CLEAN
            # =================================================

            self.clean_bowl()

            # =================================================
            # 3. PLACE BRUSH
            # =================================================

            self.place_brush()

            self.node.get_logger().info(
                "========== BRUSH CLEAN COMPLETE =========="
            )

            return True

        except Exception as e:

            self.node.get_logger().error(
                f"Brush cleaning failed: "
                f"{type(e).__name__}: "
                f"{e}"
            )

            return False

        finally:

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

    rclpy.init(
        args=args
    )

    node = rclpy.create_node(
        "brush_clean",
        namespace=ROBOT_ID
    )

    DR_init.__dsr__id = ROBOT_ID
    DR_init.__dsr__model = ROBOT_MODEL
    DR_init.__dsr__node = node

    try:

        cleaner = BrushClean(
            node
        )

        cleaner.run()

    finally:

        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":

    main()
