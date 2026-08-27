"""Rinse: rinses the toilet bowl with water."""


import DR_init


ROBOT_ID = "dsr01"
ROBOT_MODEL = "m0609"


# =============================================================
# RINSE
# =============================================================

class Rinse:

    def __init__(self, node, vel=30, acc=30):

        self.node = node
        self.vel = vel
        self.acc = acc

        self.compliance_enabled = False


    # =========================================================
    # SHOWER GRIP POINTS
    # =========================================================

    def get_shower_grip_points(self):

        from DR_common2 import posj

        return {

            # 샤워기 위
            "grip1": posj(
                -22.68,
                12.59,
                102.65,
                50.78,
                93.78,
                -14.85
            ),

            # 샤워기 잡는 위치
            "grip2": posj(
                4.18,
                10.22,
                94.84,
                35.89,
                81.23,
                -1.18
            ),

            # 샤워기 들어올릴 위치
            "grip_up": posj(
                5.54,
                1.50,
                80.15,
                34.02,
                91.07,
                16.72
            ),

            # 샤워기 제자리 안전 위치
            "grip_down": posj(
                6.95,
                1.99,
                85.36,
                32.91,
                86.04,
                13.82
            ),
        }


    # =========================================================
    # SHOWER HOME
    # =========================================================

    def get_shower_home(self):

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
    # BASE HOME
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
    # RINSE WAYPOINTS
    # =========================================================

    def get_rinse_waypoints(self):

        from DR_common2 import posj

        return [

            # 시작
            posj(
                -0.01,
                -36.50,
                78.55,
                -5.84,
                82.43,
                -90.01
            ),

            # via 1
            posj(
                35.46,
                7.06,
                34.84,
                -28.72,
                108.65,
                -83.72
            ),

            # half
            posj(
                3.82,
                20.41,
                15.44,
                -16.64,
                101.7,
                -83.72
            ),

            # via 2
            posj(
                -34.93,
                14.96,
                31.92,
                14.75,
                102.92,
                -83.72
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
    # GO TO SHOWER HOME
    # =========================================================

    def go_shower_home(self):

        from DSR_ROBOT2 import (
            movej,
            wait,
        )

        self.node.get_logger().info(
            "Move to shower HOME"
        )

        movej(
            self.get_shower_home(),
            vel=self.vel,
            acc=self.acc
        )

        wait(1.0)


    # =========================================================
    # GRIP SHOWER
    # =========================================================

    def grip_shower(self):

        from DSR_ROBOT2 import (
            movej,
            wait,
        )

        points = self.get_shower_grip_points()

        self.node.get_logger().info(
            "========== GRIP SHOWER =========="
        )

        self.gripper_open()

        movej(
            points["grip1"],
            vel=self.vel,
            acc=self.acc
        )

        wait(1.0)

        movej(
            points["grip2"],
            vel=self.vel,
            acc=self.acc
        )

        wait(1.0)

        self.gripper_close()

        movej(
            points["grip_up"],
            vel=self.vel,
            acc=self.acc
        )

        wait(1.0)


    # =========================================================
    # MOVE TO RINSE START
    # =========================================================

    def move_to_start(self):

        from DSR_ROBOT2 import (
            movej,
            wait,
        )

        waypoints = self.get_rinse_waypoints()

        self.node.get_logger().info(
            "Move to rinse start"
        )

        movej(
            waypoints[0],
            vel=self.vel,
            acc=self.acc
        )

        wait(1.0)


    # =========================================================
    # RINSE
    # =========================================================

    def apply_rinse(self):

        from DSR_ROBOT2 import (
            movesj,
            wait,
        )

        waypoints = self.get_rinse_waypoints()

        self.node.get_logger().info(
            "========== RINSE BOWL =========="
        )

        self.move_to_start()

        wait(1.0)

        rinse_path = [
            waypoints[0],
            waypoints[1],
            waypoints[2],
            waypoints[3],
            waypoints[0],
        ]

        movesj(
            rinse_path,
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
    # RELEASE SHOWER
    # =========================================================

    def release_shower(self):

        from DSR_ROBOT2 import (
            movej,
            wait,
            set_desired_force,
            release_force,
            DR_FC_MOD_ABS,
        )

        points = self.get_shower_grip_points()

        self.node.get_logger().info(
            "========== RELEASE SHOWER =========="
        )

        # =====================================================
        # 1. Move to upper return position
        # =====================================================

        movej(
            points["grip_up"],
            vel=self.vel,
            acc=self.acc
        )

        wait(1.5)

        # =====================================================
        # 2. Move to safe lower return position
        # =====================================================

        movej(
            points["grip_down"],
            vel=10,
            acc=10
        )

        wait(0.5)

        # =====================================================
        # 3. Compliance ON
        # =====================================================

        self.enable_compliance()

        try:

            # =================================================
            # 4. Apply downward force
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

            wait(9.0)

            # =================================================
            # 5. Release force
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
            # 반드시 compliance OFF
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
        # 6. Release shower
        # =====================================================

        self.gripper_open()

        self.node.get_logger().info(
            "Shower released"
        )


    # =========================================================
    # GO TO BASE
    # =========================================================

    def go_to_base(self):

        from DSR_ROBOT2 import (
            movej,
            wait,
        )

        points = self.get_shower_grip_points()

        self.node.get_logger().info(
            "Move to BASE HOME"
        )

        movej(
            points["grip_up"],
            vel=self.vel,
            acc=self.acc
        )

        wait(1.0)

        movej(
            self.get_base_home(),
            vel=self.vel,
            acc=self.acc
        )

        wait(1.0)


    # =========================================================
    # RUN
    # =========================================================

    def run(self):

        self.node.get_logger().info(
            "========== RINSE START =========="
        )

        try:

            # =================================================
            # 1. Shower home
            # =================================================

            self.go_shower_home()
            
            # =================================================
            # 2. Gripper open
            # =================================================

            self.gripper_open()

            # =================================================
            # 3. Pick shower
            # =================================================

            self.grip_shower()

            # =================================================
            # 4. Shower home
            # =================================================

            self.go_shower_home()

            # =================================================
            # 5. Rinse toilet
            # =================================================

            self.apply_rinse()

            # =================================================
            # 6. Shower home
            # =================================================

            self.go_shower_home()

            # =================================================
            # 7. Return shower
            # =================================================

            self.release_shower()

            # =================================================
            # 8. Base home
            # =================================================

            self.go_to_base()

            self.node.get_logger().info(
                "========== RINSE COMPLETE =========="
            )

            return True

        except Exception as e:

            self.node.get_logger().error(
                f"Rinse failed: "
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
        "rinse",
        namespace=ROBOT_ID
    )

    # =========================================================
    # Doosan initialization
    # =========================================================

    DR_init.__dsr__id = ROBOT_ID
    DR_init.__dsr__model = ROBOT_MODEL
    DR_init.__dsr__node = node

    # 반드시 DR_init 설정 이후
    import DSR_ROBOT2

    try:

        node.get_logger().info(
            "========== RINSE STANDALONE START =========="
        )

        rinse = Rinse(
            node
        )

        success = rinse.run()

        node.get_logger().info(
            f"Rinse result = {success}"
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