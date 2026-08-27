"""ROS 2 node for the HMI.

Subscribes to the status published by toilet_cleaning's cleaning_manager and
offers a direct move_stop call to the Doosan controller for emergency stop.
"""

import rclpy

from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy

from dsr_msgs2.srv import MoveStop

from toilet_cleaning_interfaces.msg import CleaningStatus


ROBOT_ID = "dsr01"

# cleaning_manager runs in the dsr01 namespace and publishes "cleaning/status".
STATUS_TOPIC = f"/{ROBOT_ID}/cleaning/status"

MOVE_STOP_SERVICE = (
    f"/{ROBOT_ID}/dsr_controller2/motion/move_stop"
)

# DR_QSTOP_STO(0): quick stop, stop category 1 without Safe Torque Off.
STOP_MODE_QUICK = 0


# =============================================================
# ROBOT NODE
# =============================================================

class RobotNode(Node):

    def __init__(self, on_status=None, on_log=None):

        super().__init__("toilet_hmi_node")

        # Callbacks are the GUI's queued signal emitters, so nothing here
        # ever touches a widget from the executor thread.
        self._on_status = on_status
        self._on_log = on_log

        # =====================================================
        # Cleaning status subscription
        #
        # Must match the manager's QoS, otherwise no messages
        # are delivered. TRANSIENT_LOCAL also replays the last
        # status to a late-joining HMI.
        # =====================================================

        status_qos = QoSProfile(depth=1)
        status_qos.reliability = ReliabilityPolicy.RELIABLE
        status_qos.durability = DurabilityPolicy.TRANSIENT_LOCAL

        self.status_subscription = self.create_subscription(
            CleaningStatus,
            STATUS_TOPIC,
            self.status_callback,
            status_qos,
        )

        # =====================================================
        # Doosan move_stop service
        # =====================================================

        self.move_stop_client = self.create_client(
            MoveStop,
            MOVE_STOP_SERVICE
        )

        self.get_logger().info(
            f"Toilet HMI node started, listening on {STATUS_TOPIC}"
        )

    # =========================================================
    # Callbacks
    #
    # The GUI is built after this node, so it wires its queued
    # signal emitters in here.
    # =========================================================

    def set_callbacks(self, on_status=None, on_log=None):

        if on_status is not None:
            self._on_status = on_status

        if on_log is not None:
            self._on_log = on_log

    # =========================================================
    # Cleaning Status Callback
    #
    # Runs on the executor thread. _on_status is a queued Qt
    # signal emitter, so no widget is touched from here.
    # =========================================================

    def status_callback(self, msg):

        if self._on_status is not None:

            self._on_status(msg)

    # =========================================================
    # Emergency Stop
    # =========================================================

    def request_move_stop(self):

        if not self.move_stop_client.service_is_ready():

            self.log(
                f"{MOVE_STOP_SERVICE} is not available"
            )

            return False

        request = MoveStop.Request()
        request.stop_mode = STOP_MODE_QUICK

        future = self.move_stop_client.call_async(
            request
        )

        future.add_done_callback(
            self.move_stop_response_callback
        )

        self.log(
            "Robot move_stop requested"
        )

        return True

    # =========================================================
    # Move Stop Response
    # =========================================================

    def move_stop_response_callback(self, future):

        try:

            response = future.result()

            if response.success:

                self.log(
                    "Robot move_stop SUCCESS"
                )

            else:

                self.log(
                    "Robot move_stop FAILED"
                )

        except Exception as e:

            self.log(
                f"move_stop service error: "
                f"{type(e).__name__}: {e}"
            )

    # =========================================================
    # Log
    # =========================================================

    def log(self, text):

        self.get_logger().info(
            str(text)
        )

        if self._on_log is not None:

            self._on_log(str(text))

    # =========================================================
    # Shutdown
    # =========================================================

    def shutdown(self):

        self.get_logger().info(
            "ROS shutdown"
        )


# =============================================================
# MAIN
# =============================================================

def main(args=None):

    rclpy.init(args=args)

    node = RobotNode()

    try:

        rclpy.spin(node)

    except KeyboardInterrupt:

        pass

    finally:

        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":

    main()
