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
        #
        # 변기 위 안전 위치
        #

        self.clean_above_x = 483.47
        self.clean_above_y = -50.60
        self.clean_above_z = 411.46

        self.clean_above_rx = 129.41
        self.clean_above_ry = -166.45
        self.clean_above_rz = 61.73

        # =====================================================
        # 3. CLEAN CENTER
        # =====================================================
        #
        # 첫 번째 사진 CENTER
        #

        self.center_x = 494.68
        self.center_y = -76.03
        self.center_z = 268.77

        # =====================================================
        # 4. CLEANING ORIENTATION
        # =====================================================
        #
        # 브러시를 수직으로 잡고 있던 orientation.
        #
        # 청소 중 이 orientation을 기본 자세로 유지한다.
        #
        # Tool Z rotation scrub은 move_periodic()에서 처리.
        #

        self.clean_rx = 170.08
        self.clean_ry = 179.75
        self.clean_rz = 174.90

        # =====================================================
        # 5. WALL POINTS
        # =====================================================
        #
        # 실제 변기 둘레를 닦는 순서로 P1 -> P8
        #
        #
        #                 P1
        #
        #          P8             P2
        #
        #      P7                     P3 
        #
        #          P6             P4
        #
        #                 P5
        #
        #
        # XYZ만 사용한다.
        # orientation은 위의 clean_rx/ry/rz 사용.
        #

        self.wall_points = [

            # P1 - TOP
            [497.20, -17.26, 273.15],

            # P2 - TOP RIGHT
            [547.70, -33.13, 272.87],

            # P3 - RIGHT
            [558.64, -84.99, 273.67],

            # P4 - BOTTOM RIGHT
            [550.65, -113.86, 274.78],

            # P5 - BOTTOM
            [491.32, -125.84, 274.43],

            # P6 - BOTTOM LEFT
            [442.78, -118.35, 274.27],

            # P7 - LEFT
            [411.79, -82.39, 276.25],

            # P8 - TOP LEFT
            [427.66, -38.67, 275.68],
        ]

        # =====================================================
        # 6. Z SAFETY
        # =====================================================
        #
        # 기존 teaching Z로 움직였을 때
        # 브러시가 변기 바닥에 박혔기 때문에
        # 모든 cleaning Z를 위로 올린다.
        #
        # 아직 바닥에 닿으면:
        #
        # 20 -> 25 -> 30
        #
        # 너무 높으면:
        #
        # 20 -> 15 -> 10
        #

        self.z_safety_offset = 20.0

        # =====================================================
        # 7. CLEANING SPEED
        # =====================================================

        self.clean_vel = 10.0
        self.clean_acc = 10.0

        # =====================================================
        # 8. SEGMENT SETTINGS
        # =====================================================
        #
        # P1 -> P2 사이를 몇 개의 작은 위치로 나눌지.
        #
        # 각 중간 위치마다:
        #
        # MoveL
        #   ↓
        # Tool-Z rotation scrub
        #   ↓
        # MoveL
        #   ↓
        # Tool-Z rotation scrub
        #

        self.points_per_segment = 3

        # =====================================================
        # 9. ROTATION SCRUB
        # =====================================================
        #
        # Tool Z축 기준:
        #
        #        ↺ ↻
        #         │
        #         │ brush
        #
        # +-3 degree로 시작
        #

        self.scrub_angle = 5.0

        # 한 왕복에 걸리는 시간
        self.scrub_period = 0.5

        # 한 위치에서 몇 번 왕복할지
        self.scrub_repeat = 2

        # =====================================================
        # 10. WALL FORCE
        # =====================================================
        #
        # 중요:
        #
        # 지금은 OFF.
        #
        # 먼저:
        #
        # 1. Z 안전 확인
        # 2. P1~P8 경로 확인
        # 3. Tool-Z scrub 확인
        #
        # 이후에:
        #
        # 1.0 -> 2.0 N
        #
        # 정도로 테스트.
        #

        self.wall_force = 0.0

        # =====================================================
        # 11. COMPLIANCE
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

        from DSR_ROBOT2 import (
            set_digital_output,
            wait,
        )

        self.node.get_logger().info("Gripper OPEN")

        set_digital_output(1, 0)
        set_digital_output(2, 1)

        wait(0.3)

    def gripper_close(self):
        """
        Gripper CLOSE.
        """

        from DSR_ROBOT2 import (
            set_digital_output,
            wait,
        )

        self.node.get_logger().info("Gripper CLOSE")

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
        """
        브러시 잡는 위치 바로 위.

        X/Y/orientation은 그대로 두고
        BASE Z만 +100 mm.
        """

        from DSR_ROBOT2 import posx, posj

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
        """
        브러시 잡는 위치 바로 위.
        """

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
        """
        브러시 잡는 위치
        """

        from DSR_ROBOT2 import posj

        self.node.get_logger().info(
            "Get brush approach posej"
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
        """
        위에서 아래로 내려가 브러시를 잡는다.
        Approach -> Gripper OPEN -> Pick -> Gripper CLOSE -> Lift
        """

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

        # -----------------------------------------------------
        # 1. 브러시 위로 이동
        # -----------------------------------------------------

        self.node.get_logger().info(
            "Move above brush"
        )

        movej(
            approach_j,
            vel=10.0,
            acc=10.0,
        )

        # -----------------------------------------------------
        # 2. Gripper open
        # -----------------------------------------------------

        self.gripper_open()

        # -----------------------------------------------------
        # 3. 위 -> 아래
        # -----------------------------------------------------

        wait(0.5)

        self.node.get_logger().info(
            "Move down to brush"
        )

        movej(
            pick_j,
            vel=10.0,
            acc=10.0,
        )

        wait(0.5)

        # -----------------------------------------------------
        # 4. Brush 잡기
        # -----------------------------------------------------

        self.gripper_close()

        wait(0.5)

        # -----------------------------------------------------
        # 5. 수직으로 올리기
        # -----------------------------------------------------

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
        """
        청소 후 원래 위치로 브러시를 돌려놓는다.

        위에서 아래로 내려놓음.
        """

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

        # -----------------------------------------------------
        # 1. 보관 위치 위
        # -----------------------------------------------------

        movej(
            approach_j,
            vel=self.vel,
            acc=self.acc,
        )

        # -----------------------------------------------------
        # 2. 위 -> 아래
        # -----------------------------------------------------

        wait(0.5)

        movej(
            pick_j,
            vel=self.vel,
            acc=self.acc,
        )

        wait(0.5)

        # -----------------------------------------------------
        # 3. 놓기
        # -----------------------------------------------------

        self.gripper_open()

        wait(0.5)

        # -----------------------------------------------------
        # 4. 그리퍼만 수직 상승
        # -----------------------------------------------------

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
    # SAFE CLEAN CENTER
    # =========================================================

    def get_clean_center_pose(self):
        """
        Center의 X/Y는 그대로.

        바닥에 박히는 것을 막기 위해
        center Z에 safety offset을 더한다.
        """

        from DSR_ROBOT2 import posx

        safe_z = (
            self.center_z
            + self.z_safety_offset
        )

        self.node.get_logger().info(
            f"Safe CENTER = "
            f"({self.center_x:.2f}, "
            f"{self.center_y:.2f}, "
            f"{safe_z:.2f})"
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
        실제 teaching point의 X/Y는 유지.

        Z만 safety offset 만큼 위로 올린다.
        """

        return [
            point[0],
            point[1],
            point[2] + self.z_safety_offset,
        ]

    # =========================================================
    # GET WALL POSE
    # =========================================================

    def get_wall_pose(self, point):
        from DSR_ROBOT2 import posx

        safe_point = self.get_safe_wall_point(
            point
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
    # CREATE INTERMEDIATE WALL POINTS
    # =========================================================

    def make_segment_points(
        self,
        p1,
        p2,
    ):
        """
        P1 -> P2 사이를 작은 MoveL point로 나눈다.

        예:

        P1 ---- o ---- o ---- o ---- o ---- P2

        각 o에서 Tool-Z rotation scrub 실행.
        """

        from DSR_ROBOT2 import posx

        points = []

        for i in range(
            1,
            self.points_per_segment + 1,
        ):

            t = (
                i
                / self.points_per_segment
            )

            # -------------------------------------------------
            # X interpolation
            # -------------------------------------------------

            x = (
                p1[0]
                + (p2[0] - p1[0]) * t
            )

            # -------------------------------------------------
            # Y interpolation
            # -------------------------------------------------

            y = (
                p1[1]
                + (p2[1] - p1[1]) * t
            )

            # -------------------------------------------------
            # Original Z interpolation
            # -------------------------------------------------

            original_z = (
                p1[2]
                + (p2[2] - p1[2]) * t
            )

            # -------------------------------------------------
            # Safety Z
            # -------------------------------------------------

            z = (
                original_z
                + self.z_safety_offset
            )

            target = posx(
                x,
                y,
                z,
                self.clean_rx,
                self.clean_ry,
                self.clean_rz,
            )

            points.append(
                target
            )

        return points

    # =========================================================
    # ROTATION SCRUB
    # =========================================================

    def scrub_rotation(self):
        """
        현재 XYZ 위치는 유지하고
        Tool Z축을 기준으로 브러시를 좌우 회전.

                    │
                    │
                    │
                   brush
                ↺       ↻

        Tool Z축과 실제 브러시 축이 일치해야
        원하는 동작이 나온다.
        """

        from DSR_ROBOT2 import (
            move_periodic,
            DR_TOOL,
        )

        if self.scrub_angle <= 0.0:
            return

        self.node.get_logger().info(
            f"Rotation scrub | "
            f"±{self.scrub_angle:.1f} deg"
        )

        move_periodic(
            amp=[
                0.0,                # Tool X
                0.0,                # Tool Y
                0.0,                # Tool Z
                0.0,                # Tool RX
                0.0,                # Tool RY
                self.scrub_angle,   # Tool RZ
            ],

            period=self.scrub_period,

            atime=0.2,

            repeat=self.scrub_repeat,

            ref=DR_TOOL,
        )

    # =========================================================
    # COMPLIANCE ON
    # =========================================================

    def enable_compliance(self):
        """
        중요:

        set_ref_coord()는 compliance 들어가기 전에
        여기서 딱 한 번만 호출한다.

        이전에 발생한:

        TASK_COMPLIANCE_CONTROL
        rejected eSetGlobalRefCoord

        문제를 피하기 위해
        apply_wall_force()에서는 set_ref_coord()를
        다시 호출하지 않는다.
        """

        from DSR_ROBOT2 import (
            task_compliance_ctrl,
            set_ref_coord,
            DR_BASE,
        )

        self.node.get_logger().info(
            "Compliance ON"
        )

        # -----------------------------------------------------
        # 반드시 compliance 전에 설정
        # -----------------------------------------------------

        set_ref_coord(
            DR_BASE
        )

        task_compliance_ctrl(
            stx=[
                500.0,     # X
                500.0,     # Y
                3000.0,    # Z
                200.0,     # RX
                200.0,     # RY
                200.0,     # RZ
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
        p2,
    ):
        """
        P1 -> P2의 진행 방향 tangent를 구한 후,
        그 방향에 수직인 wall normal을 계산한다.

        두 normal 중 CENTER 반대쪽을 선택한다.
        """

        dx = (
            p2[0] - p1[0]
        )

        dy = (
            p2[1] - p1[1]
        )

        length = math.sqrt(
            dx * dx
            + dy * dy
        )

        if length < 1e-6:
            raise ValueError(
                "Wall points are too close."
            )

        # -----------------------------------------------------
        # tangent
        # -----------------------------------------------------

        tx = dx / length
        ty = dy / length

        # -----------------------------------------------------
        # perpendicular normal
        # -----------------------------------------------------

        nx = -ty
        ny = tx

        # -----------------------------------------------------
        # Segment midpoint
        # -----------------------------------------------------

        mid_x = (
            p1[0] + p2[0]
        ) / 2.0

        mid_y = (
            p1[1] + p2[1]
        ) / 2.0

        # -----------------------------------------------------
        # CENTER -> WALL
        # -----------------------------------------------------

        vx = (
            mid_x
            - self.center_x
        )

        vy = (
            mid_y
            - self.center_y
        )

        # -----------------------------------------------------
        # 현재 normal이 center 쪽이면 반대로 뒤집음
        # -----------------------------------------------------

        dot = (
            nx * vx
            + ny * vy
        )

        if dot < 0:
            nx = -nx
            ny = -ny

        return nx, ny

    # =========================================================
    # APPLY WALL FORCE
    # =========================================================

    def apply_wall_force(
        self,
        p1,
        p2,
    ):
        """
        현재 segment의 벽 방향으로 force 적용.

        wall_force == 0이면 아무것도 하지 않는다.

        중요:
        여기서는 set_ref_coord()를 호출하지 않는다.
        """

        if self.wall_force <= 0.0:
            return

        from DSR_ROBOT2 import (
            set_desired_force,
            DR_FC_MOD_REL,
        )

        nx, ny = (
            self.calculate_wall_normal(
                p1,
                p2,
            )
        )

        fx = (
            nx
            * self.wall_force
        )

        fy = (
            ny
            * self.wall_force
        )

        self.node.get_logger().info(
            f"Wall force | "
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
    # CLEAN ONE WALL SEGMENT
    # =========================================================

    def clean_wall_segment(
        self,
        p1,
        p2,
        segment_number,
    ):
        """
        P1 -> P2 청소.

        각 중간 위치마다:

        MoveL
          ↓
        Tool-Z rotation scrub
          ↓
        MoveL
          ↓
        Tool-Z rotation scrub
        """

        from DSR_ROBOT2 import (
            movel,
            DR_BASE,
        )

        self.node.get_logger().info(
            "--------------------------------"
        )

        self.node.get_logger().info(
            f"CLEAN SEGMENT {segment_number}"
        )

        # -----------------------------------------------------
        # Wall force
        # -----------------------------------------------------

        if self.wall_force > 0.0:

            self.apply_wall_force(
                p1,
                p2,
            )

        # -----------------------------------------------------
        # Generate intermediate points
        # -----------------------------------------------------

        targets = (
            self.make_segment_points(
                p1,
                p2,
            )
        )

        # -----------------------------------------------------
        # Move + scrub
        # -----------------------------------------------------

        for i, target in enumerate(
            targets
        ):

            self.node.get_logger().info(
                f"Segment {segment_number} | "
                f"Point {i + 1}/{len(targets)}"
            )

            # ---------------------------------------------
            # 벽 따라 조금 이동
            # ---------------------------------------------

            movel(
                target,
                vel=self.clean_vel,
                acc=self.clean_acc,
                ref=DR_BASE,
            )

            # ---------------------------------------------
            # 현재 위치에서 회전 scrub
            # ---------------------------------------------

            self.scrub_rotation()

    # =========================================================
    # CLEAN BOWL
    # =========================================================

    def clean_bowl(self):
        """
        Cleaning sequence:

                      ABOVE
                        ↓
                  SAFE CENTER
                        ↓
                       P1

        P1 -- scrub -- scrub -- scrub --> P2
        P2 -- scrub -- scrub -- scrub --> P3
        P3 -- scrub -- scrub -- scrub --> P4
        P4 -- scrub -- scrub -- scrub --> P5
        P5 -- scrub -- scrub -- scrub --> P6
        P6 -- scrub -- scrub -- scrub --> P7
        P7 -- scrub -- scrub -- scrub --> P8
        P8 -- scrub -- scrub -- scrub --> P1

                        ↓
                  SAFE CENTER
                        ↓
                      ABOVE
        """

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
        # 1. ABOVE TOILET
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
            "Move to SAFE center"
        )

        movel(
            center,
            vel=self.clean_vel,
            acc=self.clean_acc,
            ref=DR_BASE,
        )

        wait(0.5)

        # =====================================================
        # 3. SAFE CENTER -> SAFE P1
        # =====================================================

        first_point = (
            self.wall_points[0]
        )

        first_pose = (
            self.get_wall_pose(
                first_point
            )
        )

        self.node.get_logger().info(
            "Move SAFE center -> SAFE P1"
        )

        movel(
            first_pose,
            vel=self.clean_vel,
            acc=self.clean_acc,
            ref=DR_BASE,
        )

        wait(0.5)

        # =====================================================
        # 4. FORCE / COMPLIANCE
        # =====================================================

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
            # 5. CLEAN FULL TOILET WALL
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
                    i + 1,
                )

            # =================================================
            # 6. FORCE OFF
            # =================================================

            if use_force_control:

                self.node.get_logger().info(
                    "Release wall force"
                )

                release_force()

                wait(0.3)

        finally:

            # -------------------------------------------------
            # Error 발생해도 Force 해제
            # -------------------------------------------------

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
        """
        Full sequence:

        Pick brush
            ↓
        Clean toilet
            ↓
        Place brush
        """

        self.node.get_logger().info(
            "========== BRUSH CLEAN START =========="
        )

        try:

            # -------------------------------------------------
            # 1. Brush pickup
            # -------------------------------------------------

            self.pick_brush()

            # -------------------------------------------------
            # 2. Clean toilet
            # -------------------------------------------------

            self.clean_bowl()

            # -------------------------------------------------
            # 3. Return brush
            # -------------------------------------------------

            self.place_brush()

            self.node.get_logger().info(
                "========== BRUSH CLEAN COMPLETE =========="
            )

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