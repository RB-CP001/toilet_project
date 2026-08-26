"""Cleaning Manager: controls the full toilet cleaning sequence."""

from enum import Enum, auto

import rclpy
from rclpy.node import Node

import DR_init


ROBOT_ID = "dsr01"
ROBOT_MODEL = "m0609"


# =============================================================
# DOOSAN ROBOT SETUP
# =============================================================

def setup_doosan(node):
    """
    Configure Doosan robot before importing DSR_ROBOT2.
    This function is outside the class, so name mangling does not occur.
    """

    DR_init.__dsr__id = ROBOT_ID
    DR_init.__dsr__model = ROBOT_MODEL
    DR_init.__dsr__node = node


# =============================================================
# CLEANING STATE
# =============================================================

class CleaningState(Enum):

    IDLE = auto()

    DETECT_LID = auto()

    OPEN_LID = auto()

    APPLY_BLEACH = auto()

    BRUSH_CLEAN = auto()

    RINSE = auto()

    FINISH = auto()

    DONE = auto()

    ERROR = auto()


# =============================================================
# CLEANING MANAGER
# =============================================================

class CleaningManager(Node):

    def __init__(self):

        super().__init__(
            "cleaning_manager",
            namespace=ROBOT_ID
        )

        # =====================================================
        # 1. Setup Doosan first
        # =====================================================

        setup_doosan(self)

        self.get_logger().info(
            f"DR_init id = "
            f"{getattr(DR_init, '__dsr__id')}"
        )

        self.get_logger().info(
            f"DR_init model = "
            f"{getattr(DR_init, '__dsr__model')}"
        )

        self.get_logger().info(
            f"DR_init node = "
            f"{getattr(DR_init, '__dsr__node')}"
        )

        # =====================================================
        # 2. Import DSR_ROBOT2 AFTER setup_doosan()
        # =====================================================

        import DSR_ROBOT2

        self.get_logger().info(
            "DSR_ROBOT2 initialized"
        )

        # =====================================================
        # 3. Import cleaning modules
        # =====================================================

        from .detect_lid import DetectLid
        from .open_lid import OpenLid
        from .apply_bleach import ApplyBleach
        from .brush_clean import BrushClean
        from .rinse import Rinse
        from .finish import Finish

        # =====================================================
        # 4. State
        # =====================================================

        self.state = CleaningState.IDLE

        # =====================================================
        # 5. Cleaning objects
        # =====================================================

        self.detect_lid = DetectLid(self)
        self.open_lid = OpenLid(self)
        self.apply_bleach = ApplyBleach(self)
        self.brush_clean = BrushClean(self)
        self.rinse = Rinse(self)
        self.finish = Finish(self)

    # =========================================================
    # SET STATE
    # =========================================================

    def set_state(self, new_state):

        self.state = new_state

        self.get_logger().info(
            f"STATE -> {self.state.name}"
        )


    # =========================================================
    # RUN
    # =========================================================

    def run(self):

        self.get_logger().info(
            "========== START CLEANING =========="
        )

        # =====================================================
        # START FROM DETECT LID
        # =====================================================

        self.set_state(
            CleaningState.DETECT_LID
        )

        while rclpy.ok():

            try:

                # =============================================
                # DETECT LID
                # =============================================
                if self.state == CleaningState.DETECT_LID:

                    lid_detected = self.detect_lid.run()

                    if lid_detected:
                        self.set_state(CleaningState.OPEN_LID)
                    else:
                        self.set_state(CleaningState.APPLY_BLEACH)

                # =============================================
                # OPEN LIDD
                # =============================================
                elif self.state == CleaningState.OPEN_LID:

                    success = self.open_lid.run()

                    if success:
                        self.set_state(CleaningState.APPLY_BLEACH)
                    else:
                        self.set_state(CleaningState.ERROR)



                # =============================================
                # APPLY BLEACH
                # =============================================
                elif self.state == CleaningState.APPLY_BLEACH:

                    success = self.apply_bleach.run()

                    if success:
                        self.set_state(
                            CleaningState.BRUSH_CLEAN
                        )

                    else:
                        self.set_state(
                            CleaningState.ERROR
                        )

                # =============================================
                # BRUSH CLEAN
                # =============================================

                elif self.state == CleaningState.BRUSH_CLEAN:

                    success = self.brush_clean.run()

                    if success:
                        self.set_state(
                            CleaningState.RINSE
                        )
                    else:
                        self.set_state(
                            CleaningState.ERROR
                        )
                        
                # =============================================
                # RINSE
                # =============================================

                elif self.state == CleaningState.RINSE:

                    success = self.rinse.run()

                    if success:
                        self.set_state(
                            CleaningState.FINISH
                        )
                    else:
                        self.set_state(
                            CleaningState.ERROR
                        )

                # =============================================
                # FINISH
                # =============================================
                elif self.state == CleaningState.RINSE:

                    success = self.rinse.run()

                    if success:
                        self.set_state(
                            CleaningState.FINISH
                        )
                    else:
                        self.set_state(
                            CleaningState.ERROR
                        )

                # =============================================
                # FINISH
                # =============================================
                elif self.state == CleaningState.FINISH:

                    success = self.finish.run()

                    if success:
                        self.set_state(
                            CleaningState.DONE
                        )
                    else:
                        self.set_state(
                            CleaningState.ERROR
                        )
                # =============================================
                # DONE
                # =============================================

                elif self.state == CleaningState.DONE:

                    self.get_logger().info(
                        "========== CLEANING COMPLETE =========="
                    )

                    break


                # =============================================
                # ERROR
                # =============================================

                elif self.state == CleaningState.ERROR:

                    self.get_logger().error(
                        "Cleaning stopped because of an error."
                    )

                    break


            except Exception as e:

                self.get_logger().error(
                    f"Error in state {self.state.name}: "
                    f"{type(e).__name__}: {e}"
                )

                self.set_state(
                    CleaningState.ERROR
                )


# =============================================================
# MAIN
# =============================================================

def main(args=None):

    rclpy.init(
        args=args
    )

    manager = CleaningManager()

    try:

        manager.run()

    except KeyboardInterrupt:

        manager.get_logger().info(
            "Cleaning interrupted by user"
        )

    finally:

        manager.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":

    main()