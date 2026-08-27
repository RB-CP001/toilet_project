"""Apply Bleach: applies bleach to the toilet bowl."""

import DR_init


ROBOT_ID = "dsr01"
ROBOT_MODEL = "m0609"


# =============================================================
# APPLY BLEACH
# =============================================================

class ApplyBleach:

    def __init__(self, node, vel=30, acc=30):

        self.node = node
        self.vel = vel
        self.acc = acc

        self.compliance_enabled = False


    # =========================================================
    # BLEACH GRIP POINTS
    # =========================================================

    def get_bleach_grip_points(self):

        from DR_common2 import posj

        return {

            # 락스 잡으러 가는 중간 위치
            "grip1": posj(
                32.0,
                -2.0,
                88.0,
                -22.0,
                55.0,
                -90.0
            ),

            # 락스 잡는 위치
            "grip2": posj(
                26.85,
                11.27,
                93.88,
                -28.31,
                37.86,
                -45.17
            ),

            # 락스를 들고 올라온 위치
            "grip_up": posj(
                28.32,
                -0.66,
                91.07,
                -34.43,
                38.63,
                -45.19
            ),
        }


    # =========================================================
    # BLEACH HOME
    # =========================================================

    def get_bleach_home(self):

        from DR_common2 import posj

        return posj(
            0.0,
            -10.5,
            50.0,
            0.0,
            90.0,
            -90.0
        )


    # =========================================================
    # ROBOT BASE HOME
    # =========================================================

    def get_base_home(self):

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
    # BLEACH APPLY WAYPOINTS
    # =========================================================

    def get_bleach_waypoints(self):

        from DR_common2 import posj

        return [

            # 시작 위치
            posj(
                -1.35,
                8.13,
                64.05,
                -6.94,
                124.30,
                -83.79
            ),

            # via 1
            posj(
                5.47,
                19.90,
                51.20,
                -8.61,
                124.55,
                -83.72
            ),

            # 반대쪽
            posj(
                3.18,
                29.13,
                38.96,
                -15.90,
                126.98,
                -83.71
            ),

            # via 2
            posj(
                -0.25,
                18.08,
                54.38,
                -15.86,
                123.52,
                -83.71
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

        wait(1.0)


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
    # GO TO BLEACH HOME
    # =========================================================

    def go_bleach_home(self):

        from DSR_ROBOT2 import (
            movej,
            wait,
        )

        self.node.get_logger().info(
            "Move to bleach HOME"
        )

        movej(
            self.get_bleach_home(),
            vel=self.vel,
            acc=self.acc
        )

        wait(1.0)


    # =========================================================
    # GO TO BASE HOME
    # =========================================================

    def go_to_base(self):

        from DSR_ROBOT2 import (
            movej,
            wait,
        )

        grip_points = self.get_bleach_grip_points()

        self.node.get_logger().info(
            "Move to BASE HOME"
        )

        # 먼저 락스 보관 위치에서 안전하게 위로
        movej(
            grip_points["grip_up"],
            vel=self.vel,
            acc=self.acc
        )

        wait(1.0)

        # 공통 HOME
        movej(
            self.get_base_home(),
            vel=self.vel,
            acc=self.acc
        )

        wait(1.0)


    # =========================================================
    # GRIP BLEACH
    # =========================================================

    def grip_bleach(self):

        from DSR_ROBOT2 import (
            movej,
            wait,
        )

        grip_points = self.get_bleach_grip_points()

        self.node.get_logger().info(
            "========== GRIP BLEACH =========="
        )

        # =====================================================
        # 1. Gripper open
        # =====================================================

        self.gripper_open()

        # =====================================================
        # 2. Approach bleach
        # =====================================================

        self.node.get_logger().info(
            "Move to bleach approach"
        )

        movej(
            grip_points["grip1"],
            vel=self.vel,
            acc=self.acc
        )

        wait(1.0)

        # =====================================================
        # 3. Move to bleach grip position
        # =====================================================

        self.node.get_logger().info(
            "Move to bleach grip position"
        )

        movej(
            grip_points["grip2"],
            vel=self.vel,
            acc=self.acc
        )

        wait(1.0)

        # =====================================================
        # 4. Grip bleach
        # =====================================================

        self.gripper_close()

        # =====================================================
        # 5. Lift bleach
        # =====================================================

        self.node.get_logger().info(
            "Lift bleach"
        )

        movej(
            grip_points["grip_up"],
            vel=self.vel,
            acc=self.acc
        )

        wait(1.0)


    # =========================================================
    # MOVE TO APPLY START
    # =========================================================

    def move_to_start(self):

        from DSR_ROBOT2 import (
            movej,
            wait,
        )

        waypoints = self.get_bleach_waypoints()

        self.node.get_logger().info(
            "Move to bleach apply start"
        )

        movej(
            waypoints[0],
            vel=self.vel,
            acc=self.acc
        )

        wait(1.0)


    # =========================================================
    # APPLY BLEACH
    # =========================================================

    def apply(self):

        from DSR_ROBOT2 import (
            movesj,
            wait,
        )

        waypoints = self.get_bleach_waypoints()

        self.node.get_logger().info(
            "========== APPLY BLEACH =========="
        )

        # =====================================================
        # 1. Move to start
        # =====================================================

        self.move_to_start()

        wait(1.0)

        # =====================================================
        # 2. Create full bleach path
        # =====================================================

        bleach_path = [
            waypoints[0],
            waypoints[1],
            waypoints[2],
            waypoints[3],
            waypoints[0],
        ]

        # =====================================================
        # 3. Follow path
        # =====================================================

        self.node.get_logger().info(
            "Start bleach circular motion"
        )

        movesj(
            bleach_path,
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
    # RELEASE BLEACH
    # =========================================================

    def release_bleach(self):

        from DSR_ROBOT2 import (
            movej,
            wait,
            set_desired_force,
            release_force,
            DR_FC_MOD_ABS,
        )

        grip_points = self.get_bleach_grip_points()

        self.node.get_logger().info(
            "========== RELEASE BLEACH =========="
        )

        # =====================================================
        # 1. Move to bleach return position
        # =====================================================

        movej(
            grip_points["grip_up"],
            vel=self.vel,
            acc=self.acc
        )

        wait(1.5)

        # =====================================================
        # 2. Compliance ON
        # =====================================================

        self.enable_compliance()

        try:

            # =================================================
            # 3. Downward force
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

            # 기존 동작 그대로 9초
            wait(9.0)

            # =================================================
            # 4. Release force
            # =================================================

            self.node.get_logger().info(
                "Release force"
            )

            release_force(
                time=0.0
            )

            wait(1.0)

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
        # 5. Release bleach
        # =====================================================

        self.gripper_open()

        self.node.get_logger().info(
            "Bleach released"
        )


    # =========================================================
    # RUN
    # =========================================================

    def run(self):

        self.node.get_logger().info(
            "========== APPLY BLEACH START =========="
        )

        try:


            # =================================================
            # 1. Move to bleach HOME
            # =================================================

            self.go_bleach_home()
            
            # =================================================
            # 2. Gripper open
            # =================================================

            self.gripper_open()

            # =================================================
            # 3. Pick bleach
            # =================================================

            self.grip_bleach()

            # =================================================
            # 4. Return to bleach HOME
            # =================================================

            self.go_bleach_home()

            # =================================================
            # 5. Apply bleach
            # =================================================

            self.apply()

            # =================================================
            # 6. Return to bleach HOME
            # =================================================

            self.go_bleach_home()

            # =================================================
            # 7. Return bleach
            # =================================================

            self.release_bleach()

            # =================================================
            # 8. Return BASE HOME
            # =================================================

            self.go_to_base()

            self.node.get_logger().info(
                "========== APPLY BLEACH COMPLETE =========="
            )

            return True

        except Exception as e:

            self.node.get_logger().error(
                f"Apply bleach failed: "
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

    ROBOT_ID = "dsr01"
    ROBOT_MODEL = "m0609"

    rclpy.init(
        args=args
    )

    node = rclpy.create_node(
        "apply_bleach",
        namespace=ROBOT_ID
    )

    DR_init.__dsr__id = ROBOT_ID
    DR_init.__dsr__model = ROBOT_MODEL
    DR_init.__dsr__node = node

    # 반드시 DR_init 설정 이후
    import DSR_ROBOT2

    try:

        node.get_logger().info(
            "========== APPLY BLEACH STANDALONE START =========="
        )

        bleach = ApplyBleach(
            node
        )

        success = bleach.run()

        node.get_logger().info(
            f"Apply bleach result = {success}"
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