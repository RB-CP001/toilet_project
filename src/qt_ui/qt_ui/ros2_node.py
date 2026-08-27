"""ROS 2 node for the HMI.

Subscribes to the status published by toilet_cleaning's cleaning_manager,
watches the controller for safety events (collision, emergency stop) and
offers a direct move_stop call to the Doosan controller.
"""

import threading

import rclpy

from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy

from dsr_msgs2.msg import RobotError
from dsr_msgs2.srv import GetRobotState, MoveStop

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
# SAFETY MONITORING
#
# A collision does not stay visible in the robot state.
# OnMonitoringStateCB in dsr_controller2.cpp clears STATE_SAFE_STOP
# the moment it sees it:
#
#     case STATE_SAFE_STOP:
#         set_safe_stop_reset_type(SAFE_STOP_RESET_TYPE_DEFAULT);
#         set_robot_control(CONTROL_RESET_SAFET_STOP);
#
# so polling the state alone misses it, which is why only the
# emergency stop button (STATE_EMERGENCY_STOP, no auto reset) used
# to register. The alarm topic is the signal that cannot be missed:
# OnLogAlarm publishes one RobotError per alarm, and a delivered
# message survives a polling gap. State polling is kept alongside it
# for the states that do latch.
# =============================================================

# dsr_controller2 creates this publisher without the service prefix,
# so it lands directly in the robot namespace.
ERROR_TOPIC = f"/{ROBOT_ID}/error"

ROBOT_STATE_SERVICE = (
    f"/{ROBOT_ID}/dsr_controller2/system/get_robot_state"
)

# RobotError.level
ERROR_LEVEL_ERROR = 3

# RobotError.group
ERROR_GROUP_SAFETY_CONTROLLER = 5

ERROR_GROUP_NAME = {
    1: "SYSTEM",
    2: "MOTION",
    3: "TP",
    4: "INVERTER",
    5: "SAFETY_CONTROLLER",
}

# Numbering follows GetRobotState.srv and GetRobotStateString() in
# dsr_controller2.cpp. The comment block in RobotState.msg lists 7
# twice and is shifted from there on, so it must not be used.
ROBOT_STATE_NAME = {
    0: "INITIALIZING",
    1: "STANDBY",
    2: "MOVING",
    3: "SAFE_OFF",
    4: "TEACHING",
    5: "SAFE_STOP",
    6: "EMERGENCY_STOP",
    7: "HOMMING",
    8: "RECOVERY",
    9: "SAFE_STOP2",
    10: "SAFE_OFF2",
    15: "NOT_READY",
}

# States that hold long enough for polling to catch them.
UNSAFE_ROBOT_STATES = (3, 5, 6, 9, 10)

# get_robot_state_cb reaches the robot controller over TCP on every call,
# and it shares an executor with the motion and IO services. Polling it
# hard starves them, so this only ticks while a run is active and it ticks
# slowly. The alarm topic, not this timer, is what catches a collision.
ROBOT_STATE_POLL_SEC = 2.0


# =============================================================
# ROBOT NODE
# =============================================================

class RobotNode(Node):

    def __init__(self, on_status=None, on_log=None, on_safety=None):

        super().__init__("toilet_hmi_node")

        # Callbacks are the GUI's queued signal emitters, so nothing here
        # ever touches a widget from the executor thread.
        self._on_status = on_status
        self._on_log = on_log
        self._on_safety = on_safety

        # One collision raises several alarms and the state poll keeps
        # reporting the same state, so the stop must fire once. The latch
        # is set on the executor thread and cleared from the Qt thread.
        self._safety_lock = threading.Lock()
        self._safety_latched = False

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

        # =====================================================
        # Controller alarms
        #
        # Event driven, so a collision is caught even though the
        # controller clears the safe stop state right away.
        # Default QoS matches the publisher in dsr_controller2.
        # =====================================================

        self.error_subscription = self.create_subscription(
            RobotError,
            ERROR_TOPIC,
            self.robot_error_callback,
            100,
        )

        # =====================================================
        # Robot state poll
        #
        # Backs up the alarm topic for the states that latch:
        # emergency stop and servo off hold. Idle by default and
        # armed only while a robot process runs, so the HMI adds
        # no controller load when nothing is moving.
        # =====================================================

        self.robot_state_client = self.create_client(
            GetRobotState,
            ROBOT_STATE_SERVICE
        )

        # One request at a time. If the controller is slow to answer,
        # queueing more would make that worse.
        self._state_request_pending = False

        self.robot_state_timer = self.create_timer(
            ROBOT_STATE_POLL_SEC,
            self.poll_robot_state
        )

        self.robot_state_timer.cancel()

        self.get_logger().info(
            f"Toilet HMI node started, listening on {STATUS_TOPIC} "
            f"and {ERROR_TOPIC}"
        )

    # =========================================================
    # Callbacks
    #
    # The GUI is built after this node, so it wires its queued
    # signal emitters in here.
    # =========================================================

    def set_callbacks(self, on_status=None, on_log=None, on_safety=None):

        if on_status is not None:
            self._on_status = on_status

        if on_log is not None:
            self._on_log = on_log

        if on_safety is not None:
            self._on_safety = on_safety

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
    # Controller Alarm (executor thread)
    #
    # Filtered on level and group rather than on specific codes,
    # so this holds regardless of which alarm index a collision
    # happens to raise on this controller version.
    # =========================================================

    def robot_error_callback(self, msg):

        is_safety = (
            msg.group == ERROR_GROUP_SAFETY_CONTROLLER
            or msg.level >= ERROR_LEVEL_ERROR
        )

        group = ERROR_GROUP_NAME.get(msg.group, str(msg.group))

        detail = " / ".join(
            part for part in (msg.msg1, msg.msg2, msg.msg3) if part
        )

        if not is_safety:

            # Still worth showing, but it does not stop the run.
            self.log(
                f"[컨트롤러 알람] {group} code={msg.code} {detail}".rstrip()
            )

            return

        reason = f"[{group}] code={msg.code}"

        if detail:

            reason = f"{reason} {detail}"

        self.trigger_safety_stop(reason)

    # =========================================================
    # Robot State Poll (executor thread)
    # =========================================================

    def set_run_active(self, active):
        """Arm the state poll only while a robot process is running."""

        if active:

            self.robot_state_timer.reset()

        else:

            self.robot_state_timer.cancel()

            self._state_request_pending = False

    def poll_robot_state(self):

        # Nothing to poll for once the run is already being stopped.
        with self._safety_lock:

            if self._safety_latched:

                return

        if self._state_request_pending:

            return

        if not self.robot_state_client.service_is_ready():

            return

        self._state_request_pending = True

        future = self.robot_state_client.call_async(
            GetRobotState.Request()
        )

        future.add_done_callback(
            self.robot_state_response_callback
        )

    def robot_state_response_callback(self, future):

        self._state_request_pending = False

        try:

            response = future.result()

        except Exception as e:

            self.log(
                f"get_robot_state service error: "
                f"{type(e).__name__}: {e}"
            )

            return

        if response is None or not response.success:

            return

        state = int(response.robot_state)

        if state not in UNSAFE_ROBOT_STATES:

            return

        name = ROBOT_STATE_NAME.get(state, "UNKNOWN")

        self.trigger_safety_stop(
            f"로봇 상태 {name}({state})"
        )

    # =========================================================
    # Safety Stop
    #
    # Halts the arm from this thread rather than waiting for the
    # GUI, so a busy Qt thread cannot delay the stop.
    # =========================================================

    def trigger_safety_stop(self, reason):

        with self._safety_lock:

            if self._safety_latched:

                # Already stopping. Keep the detail in the log only.
                self.log(f"[안전] {reason}")

                return

            self._safety_latched = True

        self.get_logger().error(
            f"SAFETY STOP: {reason}"
        )

        self.request_move_stop()

        if self._on_safety is not None:

            self._on_safety(reason)

    def reset_safety_latch(self):
        """Re-arm the detector. Called from the Qt thread before a new run."""

        with self._safety_lock:

            self._safety_latched = False

    def is_safety_latched(self):

        with self._safety_lock:

            return self._safety_latched

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
