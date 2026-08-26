"""Finish: finalizes the cleaning sequence and reports completion."""

import rclpy
import DR_init


ROBOT_ID = "dsr01"
ROBOT_MODEL = "m0609"


# =============================================================
# FINISH
# =============================================================

class Finish:

    def __init__(self, node, vel=30, acc=30):

        self.node = node
        self.vel = vel
        self.acc = acc

        self.compliance_enabled = False


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
    # LID CLOSE POINTS
    # =========================================================

    def get_lid_points(self):

        from DR_common2 import posj

        return [

            # 뚜껑 닫을 위치 위
            posj(
                2.31,
                18.53,
                22.84,
                -11.57,
                87.51,
                0.00
            ),

            # 뚜껑 닫을 위치
            posj(
                2.31,
                24.80,
                26.88,
                -11.58,
                87.82,
                0.00
            ),

            # 뚜껑 닫기
            posj(
                2.48,
                24.24,
                28.54,
                -12.24,
                99.42,
                0.00
            ),
        ]


    # =========================================================
    # LEVER POINTS
    # =========================================================

    def get_lever_points(self):

        from DR_common2 import posj

        return [

            # 레버 누르기 전
            posj(
                5.58,
                31.66,
                27.65,
                -13.56,
                92.88,
                0.00
            ),

            # 레버 누름 위치
            posj(
                5.58,
                31.66,
                20.56,
                -13.56,
                92.88,
                0.00
            ),
        ]


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

        wait(1.0)


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
    # CLOSE LID
    # =========================================================

    def close_lid(self):

        from DSR_ROBOT2 import (
            movej,
            wait,
        )

        points = self.get_lid_points()

        self.node.get_logger().info(
            "========== CLOSE LID =========="
        )

        # =====================================================
        # 1. Move above lid
        # =====================================================

        self.node.get_logger().info(
            "Move above lid"
        )

        movej(
            points[0],
            vel=self.vel,
            acc=self.acc
        )

        wait(0.5)

        # =====================================================
        # 2. Move to lid
        # =====================================================

        self.node.get_logger().info(
            "Move to lid closing position"
        )

        movej(
            points[1],
            vel=20,
            acc=20
        )

        wait(0.5)

        # =====================================================
        # 3. Close lid
        # =====================================================

        self.node.get_logger().info(
            "Close lid"
        )

        movej(
            points[2],
            vel=20,
            acc=20
        )

        wait(0.5)

        self.node.get_logger().info(
            "Lid closed"
        )


    # =========================================================
    # ENABLE COMPLIANCE
    # =========================================================

    def enable_compliance(self):

        from DSR_ROBOT2 import (
            task_compliance_ctrl,
            set_stiffnessx,
        )

        self.node.get_logger().info(
            "Compliance ON"
        )

        task_compliance_ctrl()

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

        self.compliance_enabled = True


    # =========================================================
    # DISABLE COMPLIANCE
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
    # PRESS LEVER
    # =========================================================

    def press_lever(self):

        from DSR_ROBOT2 import (
            movej,
            wait,
            set_desired_force,
            release_force,
            DR_FC_MOD_ABS,
        )

        points = self.get_lever_points()

        self.node.get_logger().info(
            "========== PRESS LEVER =========="
        )

        # =====================================================
        # 1. Move in front of lever
        # =====================================================

        movej(
            points[0],
            vel=self.vel,
            acc=self.acc
        )

        wait(0.5)

        # =====================================================
        # 2. Compliance ON
        # =====================================================

        self.enable_compliance()

        try:

            # =================================================
            # 3. Press lever with force
            # =================================================

            self.node.get_logger().info(
                "Apply lever force"
            )

            set_desired_force(
                [
                    0,
                    0,
                    -40,
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

            wait(3.0)

            # =================================================
            # 4. Release force
            # =================================================

            self.node.get_logger().info(
                "Release lever force"
            )

            release_force(
                time=0.0
            )

            wait(0.5)

        finally:

            # =================================================
            # 반드시 Compliance OFF
            # =================================================

            if self.compliance_enabled:

                try:

                    self.disable_compliance()

                except Exception as e:

                    self.node.get_logger().error(
                        "Failed to release compliance: "
                        f"{e}"
                    )

        # =====================================================
        # 5. Move away from lever
        # =====================================================

        movej(
            points[0],
            vel=20,
            acc=20
        )

        wait(0.5)

        self.node.get_logger().info(
            "Lever press complete"
        )


    # =========================================================
    # RUN
    # =========================================================

    def run(self):

        self.node.get_logger().info(
            "========== FINISH START =========="
        )

        try:

            # =================================================
            # 1. HOME
            # =================================================

            self.go_home()

            # =================================================
            # 2. Close gripper
            # =================================================

            self.gripper_close()

            # =================================================
            # 3. Close toilet lid
            # =================================================

            self.close_lid()

            # =================================================
            # 4. Press flush lever
            # =================================================

            self.press_lever()

            # =================================================
            # 5. Return HOME
            # =================================================

            self.go_home()

            self.node.get_logger().info(
                "========== FINISH COMPLETE =========="
            )

            return True

        except Exception as e:

            self.node.get_logger().error(
                f"Finish failed: "
                f"{type(e).__name__}: {e}"
            )

            return False

        finally:

            # =================================================
            # Error 발생해도 compliance 해제
            # =================================================

            if self.compliance_enabled:

                try:

                    self.disable_compliance()

                except Exception as e:

                    self.node.get_logger().error(
                        "Failed to release compliance: "
                        f"{e}"
                    )


# =============================================================
# DOOSAN SETUP
# =============================================================

def setup_doosan(node):

    DR_init.__dsr__id = ROBOT_ID
    DR_init.__dsr__model = ROBOT_MODEL
    DR_init.__dsr__node = node


# =============================================================
# STANDALONE TEST
# =============================================================

def main(args=None):

    rclpy.init(
        args=args
    )

    node = rclpy.create_node(
        "finish",
        namespace=ROBOT_ID
    )

    # =========================================================
    # Doosan initialization
    # =========================================================

    setup_doosan(node)

    # 반드시 DR_init 설정 이후
    import DSR_ROBOT2

    try:

        node.get_logger().info(
            "========== FINISH STANDALONE START =========="
        )

        finish = Finish(
            node
        )

        success = finish.run()

        node.get_logger().info(
            f"Finish result = {success}"
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