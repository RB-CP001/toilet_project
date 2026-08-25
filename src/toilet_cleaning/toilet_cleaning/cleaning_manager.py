"""Cleaning Manager: controls the full toilet cleaning sequence."""

from enum import Enum, auto

import rclpy
from rclpy.node import Node

import DR_init

from .detect_lid import DetectLid
from .open_lid import OpenLid
from .apply_bleach import ApplyBleach
from .brush_clean import BrushClean
from .rinse import Rinse
from .finish import Finish


ROBOT_ID = "dsr01"
ROBOT_MODEL = "m0609"

DR_init.__dsr__id = ROBOT_ID
DR_init.__dsr__model = ROBOT_MODEL


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


class CleaningManager(Node):

    def __init__(self):
        super().__init__("cleaning_manager", namespace=ROBOT_ID)

        # Doosan Robot API가 사용할 ROS2 node
        DR_init.__dsr__node = self

        # 현재 State
        self.state = CleaningState.IDLE

        # 각 cleaning step 객체 생성
        self.detect_lid = DetectLid(self)
        self.open_lid = OpenLid(self)
        self.apply_bleach = ApplyBleach(self)
        self.brush_clean = BrushClean(self)
        self.rinse = Rinse(self)
        self.finish = Finish(self)

    def set_state(self, new_state):
        """Change and log the current cleaning state."""

        self.state = new_state
        self.get_logger().info(
            f"STATE -> {self.state.name}"
        )

    def run(self):
        """Run the complete cleaning state machine."""

        self.get_logger().info(
            "========== START CLEANING =========="
        )

        self.set_state(CleaningState.DETECT_LID)

        while rclpy.ok():

            try:

                if self.state == CleaningState.DETECT_LID:

                    lid_detected = self.detect_lid.run()

                    if lid_detected:
                        self.set_state(CleaningState.OPEN_LID)
                    else:
                        self.get_logger().info(
                            "Lid is already open. Skipping OPEN_LID."
                        )
                        self.set_state(CleaningState.APPLY_BLEACH)

                elif self.state == CleaningState.OPEN_LID:

                    self.open_lid.run()
                    self.set_state(CleaningState.APPLY_BLEACH)

                elif self.state == CleaningState.APPLY_BLEACH:

                    self.apply_bleach.run()
                    self.set_state(CleaningState.BRUSH_CLEAN)

                elif self.state == CleaningState.BRUSH_CLEAN:

                    self.brush_clean.run()
                    self.set_state(CleaningState.RINSE)

                elif self.state == CleaningState.RINSE:

                    self.rinse.run()
                    self.set_state(CleaningState.FINISH)

                elif self.state == CleaningState.FINISH:

                    self.finish.run()
                    self.set_state(CleaningState.DONE)

                elif self.state == CleaningState.DONE:

                    self.get_logger().info(
                        "========== CLEANING COMPLETE =========="
                    )
                    break

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

                self.set_state(CleaningState.ERROR)


def main(args=None):
    rclpy.init(args=args)

    manager = CleaningManager()

    try:
        manager.run()

    except KeyboardInterrupt:
        manager.get_logger().info(
            "Cleaning interrupted by user"
        )

    finally:
        manager.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()