"""Open Lid: opens the toilet lid."""

import DR_init


ROBOT_ID = "dsr01"
ROBOT_MODEL = "m0609"


# =============================================================
# OPEN LID
# =============================================================

class OpenLid:

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
    # LID POINTS
    # =========================================================

    def get_lid_points(self):

        from DR_common2 import posj

        return [

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

            # 변기 탈출 위치
            posj(
                -6.70,
                2.64,
                70.35,
                -0.63,
                26.74,
                -94.18
            ),
        ]


    # =========================================================
    # OPEN LID PATH
    # =========================================================

    def get_open_lid_points(self):

        from DR_common2 import posj

        return [

            # 1번 열린 위치
            posj(
                -9.03,
                4.32,
                77.37,
                -4.21,
                106.58,
                -92.78
            ),

            # 2번 열린 위치
            posj(
                -10.22,
                9.07,
                66.39,
                -3.23,
                115.31,
                -92.84
            ),

            # 3번 열린 위치
            posj(
                -9.08,
                16.60,
                48.42,
                -4.76,
                127.22,
                -92.84
            ),

            # 4번 열린 위치
            posj(
                -9.60,
                10.92,
                48.11,
                -2.11,
                117.35,
                -92.76
            ),

            # 5번 열린 위치
            posj(
                -8.92,
                10.73,
                40.75,
                -1.55,
                108.02,
                -92.76
            ),

            # 6번 열린 위치
            posj(
                -7.50,
                11.97,
                39.42,
                -1.57,
                97.00,
                -92.76
            ),

            # 7번 열린 위치
            posj(
                -6.17,
                15.12,
                38.76,
                -1.21,
                85.98,
                -92.76
            ),

            # 8번 열린 위치
            posj(
                -6.60,
                18.61,
                38.75,
                0.87,
                77.30,
                -92.76
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

        self.node.get_logger().info(
            "Gripper OPEN"
        )
        wait(0.5)
        
        set_digital_output(1, 0)
        set_digital_output(2, 1)

        wait(0.3)


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
    # MOVE TO LID HANDLE
    # =========================================================

    def move_to_lid(self):

        from DSR_ROBOT2 import (
            movej,
            wait,
        )

        lid_points = self.get_lid_points()

        self.node.get_logger().info(
            "Move above lid handle"
        )

        movej(
            lid_points[0],
            vel=self.vel,
            acc=self.acc
        )

        wait(1.0)

        self.node.get_logger().info(
            "Move to lid handle"
        )

        movej(
            lid_points[1],
            vel=self.vel,
            acc=self.acc
        )

        wait(1.0)


    # =========================================================
    # ENABLE COMPLIANCE
    # =========================================================

    def enable_compliance(self):

        from DSR_ROBOT2 import (
            task_compliance_ctrl,
        )

        self.node.get_logger().info(
            "Compliance ON"
        )

        task_compliance_ctrl(
            stx=[
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
    # OPEN LID MOTION
    # =========================================================

    def open_lid_motion(self):

        from DSR_ROBOT2 import (
            movej,
            wait,
        )

        open_points = self.get_open_lid_points()
        lid_points = self.get_lid_points()

        self.node.get_logger().info(
            "========== OPEN LID MOTION =========="
        )

        # =====================================================
        # Compliance ON
        # =====================================================

        self.enable_compliance()

        try:

            # =================================================
            # Follow lid opening path
            # =================================================

            for i, point in enumerate(
                open_points
            ):

                self.node.get_logger().info(
                    f"Open lid point "
                    f"{i + 1}/{len(open_points)}"
                )

                movej(
                    point,
                    vel=15,
                    acc=15
                )

                wait(0.5)

            # =================================================
            # Release lid handle
            # =================================================

            self.node.get_logger().info(
                "Lid fully opened"
            )

            self.gripper_open()

            wait(0.5)

            # =================================================
            # Escape from lid
            # =================================================

            self.node.get_logger().info(
                "Move away from lid"
            )

            movej(
                lid_points[2],
                vel=15,
                acc=15
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
                        f"Failed to release compliance: {e}"
                    )


    # =========================================================
    # RUN
    # =========================================================

    def run(self):
  
        self.node.get_logger().info(
            "========== OPEN LID START =========="
        )

        try:
                       

            # =================================================
            # 1. Home
            # =================================================

            self.go_home()
           
            # =================================================
            # 2. Gripper open
            # =================================================

            self.gripper_open()

            # =================================================
            # 3. Move to lid handle
            # =================================================

            self.move_to_lid()

            # =================================================
            # 4. Grab lid handle
            # =================================================

            self.gripper_close()

            # =================================================
            # 5. Open lid
            # =================================================

            self.open_lid_motion()

            # =================================================
            # 6. Home
            # =================================================

            self.go_home()

            self.node.get_logger().info(
                "========== OPEN LID COMPLETE =========="
            )

            return True

        except Exception as e:

            self.node.get_logger().error(
                f"Open lid failed: "
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
# STANDALONE TEST
# =============================================================

def main(args=None):

    import rclpy

    rclpy.init(
        args=args
    )

    node = rclpy.create_node(
        "open_lid",
        namespace=ROBOT_ID
    )

    # =========================================================
    # Doosan initialization
    # =========================================================

    DR_init.__dsr__id = ROBOT_ID
    DR_init.__dsr__model = ROBOT_MODEL
    DR_init.__dsr__node = node

    # 반드시 DR_init 설정 이후 import
    import DSR_ROBOT2

    try:

        node.get_logger().info(
            "========== OPEN LID STANDALONE START =========="
        )

        opener = OpenLid(
            node
        )

        success = opener.run()

        node.get_logger().info(
            f"Open lid result = {success}"
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