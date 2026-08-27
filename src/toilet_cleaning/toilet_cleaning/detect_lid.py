"""Detect Lid: detects whether the toilet lid is present."""

import DR_init


ROBOT_ID = "dsr01"
ROBOT_MODEL = "m0609"


# =============================================================
# DETECT LID
# =============================================================

class DetectLid:

    def __init__(self, node, vel=30, acc=30):

        self.node = node
        self.vel = vel
        self.acc = acc

        # =====================================================
        # Detection result
        # =====================================================

        self.fcon1 = None


    # =========================================================
    # HOME POSE
    # =========================================================

    def get_home_pose(self):

        from DR_common2 import posj

        return posj(
            0,
            0,
            50,
            0,
            90,
            0
        )


    # =========================================================
    # DETECTION POSES
    # =========================================================

    def get_detection_points(self):

        from DR_common2 import posj

        return [

            # 변기 뚜껑 위
            posj(
                -5.59,
                16.17,
                54.01,
                -4.45,
                106.05,
                -92.24
            ),

            # 변기 손잡이 위
            posj(
                -10.13,
                -2.14,
                75.49,
                -2.76,
                106.43,
                -92.76
            ),

            # 변기 손잡이 위치
            posj(
                -9.01,
                -2.77,
                90.70,
                -3.94,
                93.12,
                -92.78
            ),
        ]


    # =========================================================
    # GRIPPER OPEN
    # =========================================================

    def gripper_open(self):

        from DSR_ROBOT2 import (
            set_digital_output,
            wait,
        )


        self.node.get_logger().info("Gripper OPEN - START")

        self.node.get_logger().info("Before DO 1")
        set_digital_output(1, 0)
        self.node.get_logger().info("After DO 1")

        self.node.get_logger().info("Before DO 2")
        set_digital_output(2, 1)
        self.node.get_logger().info("After DO 2")

        self.node.get_logger().info("Before wait")
        wait(1.0)
        self.node.get_logger().info("After wait")

        self.node.get_logger().info("Gripper OPEN - DONE")

    # =========================================================
    # GRIPPER CLOSE
    # =========================================================

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
    # GO HOME
    # =========================================================

    def go_home(self):

        from DSR_ROBOT2 import movej

        self.node.get_logger().info(
            "Move HOME"
        )

        movej(
            self.get_home_pose(),
            vel=self.vel,
            acc=self.acc
        )


    # =========================================================
    # MOVE TO DETECTION POSITION
    # =========================================================

    def move_to_detection_position(self):

        from DSR_ROBOT2 import movej

        detection_points = self.get_detection_points()

        self.node.get_logger().info(
            "Move above toilet lid"
        )

        movej(
            detection_points[0],
            vel=self.vel,
            acc=self.acc
        )


    # =========================================================
    # LIFT DOWN
    # =========================================================

    def lift_down(self):

        from DSR_ROBOT2 import (
            get_current_posx,
            movel,
            DR_BASE,
        )

        self.node.get_logger().info(
            "Move down in BASE Z"
        )

        position, sol = get_current_posx(
            ref=DR_BASE
        )

        self.node.get_logger().info(
            f"Current position: {position}, sol={sol}"
        )

        move_point = [
            position[0],
            position[1],
            position[2] - 300.0,
            position[3],
            position[4],
            position[5],
        ]

        movel(
            move_point,
            vel=10.0,
            acc=10.0,
            ref=DR_BASE
        )


    # =========================================================
    # DETECT WITH FORCE
    # =========================================================

    def insert_with_force(self):

        from DSR_ROBOT2 import (
            wait,
            task_compliance_ctrl,
            set_stiffnessx,
            set_desired_force,
            release_force,
            release_compliance_ctrl,
            check_force_condition,
            DR_AXIS_Z,
            DR_FC_MOD_ABS,
            DR_BASE,
        )

        self.node.get_logger().info(
            "========== LID FORCE DETECTION =========="
        )

        compliance_enabled = False

        try:

            # =================================================
            # 1. Compliance ON
            # =================================================

            self.node.get_logger().info(
                "Compliance ON"
            )

            task_compliance_ctrl()

            compliance_enabled = True

            # =================================================
            # 2. Stiffness
            # =================================================

            set_stiffnessx(
                [
                    3000,
                    3000,
                    3000,
                    200,
                    200,
                    200
                ],
                time=0.0
            )

            # =================================================
            # 3. Z 방향 force
            # =================================================

            self.node.get_logger().info(
                "Apply downward force"
            )

            set_desired_force(
                [
                    0,
                    0,
                    -50,
                    0,
                    0,
                    0
                ],
                [
                    0,
                    0,
                    1,
                    0,
                    0,
                    0
                ],
                time=0.0,
                mod=DR_FC_MOD_ABS
            )

            # Force가 적용될 시간
            wait(5.5)

            # =================================================
            # 4. Check force
            # =================================================

            self.fcon1 = check_force_condition(
                DR_AXIS_Z,
                max=20,
                ref=DR_BASE
            )

            self.node.get_logger().info(
                f"Force condition result = {self.fcon1}"
            )

        finally:

            # =================================================
            # Force / Compliance 반드시 해제
            # =================================================

            if compliance_enabled:

                self.node.get_logger().info(
                    "Release force"
                )

                try:
                    release_force(
                        time=0.0
                    )

                except Exception as e:

                    self.node.get_logger().error(
                        f"Failed to release force: {e}"
                    )

                try:

                    release_compliance_ctrl()

                    self.node.get_logger().info(
                        "Compliance OFF"
                    )

                except Exception as e:

                    self.node.get_logger().error(
                        f"Failed to release compliance: {e}"
                    )


    # =========================================================
    # RUN
    # =========================================================

    def run(self):
    
        self.node.get_logger().info(
            "========== DETECT LID START =========="
        )

        try:



            # =================================================
            # 1. HOME
            # =================================================

            self.go_home()
            
            # =================================================
            # 2. Gripper open
            # =================================================

            self.gripper_open()

            # =================================================
            # 3. Gripper close
            # =================================================

            self.gripper_close()

            # =================================================
            # 4. Move above lid
            # =================================================

            self.move_to_detection_position()

            # =================================================
            # 5. Detect lid using force
            # =================================================

            self.insert_with_force()

            # =================================================
            # 6. Return HOME
            # =================================================

            self.go_home()

            # =================================================
            # 7. Result
            # =================================================

            if self.fcon1 == -1:

                self.node.get_logger().info(
                    "Lid detected"
                )

                return True

            else:

                self.node.get_logger().info(
                    "Lid not detected"
                )

                return False

        except Exception as e:

            self.node.get_logger().error(
                f"Lid detection failed: "
                f"{type(e).__name__}: {e}"
            )

            return False


# =============================================================
# STANDALONE TEST
# =============================================================

def main(args=None):
    
    import rclpy

    rclpy.init(
        args=args
    )

    node = rclpy.create_node(
        "detect_lid",
        namespace=ROBOT_ID
    )

    # =========================================================
    # Doosan 초기화
    # =========================================================

    DR_init.__dsr__id = ROBOT_ID
    DR_init.__dsr__model = ROBOT_MODEL
    DR_init.__dsr__node = node

    # 반드시 DR_init 설정 이후
    import DSR_ROBOT2

    try:

        node.get_logger().info(
            "========== DETECT LID STANDALONE START =========="
        )

        detector = DetectLid(
            node
        )

        lid_detected = detector.run()

        node.get_logger().info(
            f"Detect result = {lid_detected}"
        )

    except Exception as e:

        node.get_logger().error(
            f"Robot Error: "
            f"{type(e).__name__}: {e}"
        )

    finally:

        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":

    main()