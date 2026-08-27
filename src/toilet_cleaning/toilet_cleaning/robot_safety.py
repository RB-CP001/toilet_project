"""Robot safety and configuration validation."""

import rclpy

from dsr_msgs2.srv import (
    MoveStop,
    GetCurrentTool,
    GetCurrentTcp,
)


# =============================================================
# EXCEPTIONS
# =============================================================

class RobotConfigurationError(RuntimeError):
    """Raised when robot Tool/TCP configuration is invalid."""
    pass


# =============================================================
# ROBOT SAFETY
# =============================================================

class RobotSafety:

    # Doosan MoveStop mode
    DR_QSTOP = 1

    def __init__(self, node):

        self.node = node

        # =====================================================
        # MOVE STOP CLIENT
        # =====================================================

        self.stop_client = self.node.create_client(
            MoveStop,
            "dsr_controller2/motion/move_stop",
        )

        # =====================================================
        # CURRENT TOOL CLIENT
        # =====================================================

        self.tool_client = self.node.create_client(
            GetCurrentTool,
            "dsr_controller2/tool/get_current_tool",
        )

        # =====================================================
        # CURRENT TCP CLIENT
        # =====================================================

        self.tcp_client = self.node.create_client(
            GetCurrentTcp,
            "dsr_controller2/tcp/get_current_tcp",
        )

        self.node.get_logger().info(
            "RobotSafety initialized"
        )


    # =========================================================
    # GET CURRENT TOOL WITH TIMEOUT
    # =========================================================

    def get_tool_with_timeout(
        self,
        timeout_sec=2.0,
    ):

        self.node.get_logger().info(
            "Calling get_current_tool service..."
        )

        # -----------------------------------------------------
        # 1. Wait for service
        # -----------------------------------------------------

        if not self.tool_client.wait_for_service(
            timeout_sec=timeout_sec
        ):

            raise RobotConfigurationError(
                "get_current_tool service unavailable "
                f"after {timeout_sec:.1f} sec"
            )

        # -----------------------------------------------------
        # 2. Send request
        # -----------------------------------------------------

        request = GetCurrentTool.Request()

        future = self.tool_client.call_async(
            request
        )

        # -----------------------------------------------------
        # 3. Wait for response with timeout
        # -----------------------------------------------------

        rclpy.spin_until_future_complete(
            self.node,
            future,
            timeout_sec=timeout_sec,
        )

        # -----------------------------------------------------
        # 4. Timeout
        # -----------------------------------------------------

        if not future.done():

            future.cancel()

            raise RobotConfigurationError(
                "get_current_tool timeout "
                f"after {timeout_sec:.1f} sec"
            )

        # -----------------------------------------------------
        # 5. ROS service exception
        # -----------------------------------------------------

        exception = future.exception()

        if exception is not None:

            raise RobotConfigurationError(
                "get_current_tool service error: "
                f"{exception}"
            )

        # -----------------------------------------------------
        # 6. Get response
        # -----------------------------------------------------

        response = future.result()

        if response is None:

            raise RobotConfigurationError(
                "get_current_tool returned no response"
            )

        # -----------------------------------------------------
        # 7. Controller returned failure
        # -----------------------------------------------------

        if not response.success:

            raise RobotConfigurationError(
                "get_current_tool service returned success=False"
            )

        tool = response.info

        # -----------------------------------------------------
        # 8. Validate value
        # -----------------------------------------------------

        if not isinstance(tool, str) or not tool.strip():

            raise RobotConfigurationError(
                "Current Tool is empty"
            )

        self.node.get_logger().info(
            f"Current Tool = {tool}"
        )

        return tool


    # =========================================================
    # GET CURRENT TCP WITH TIMEOUT
    # =========================================================

    def get_tcp_with_timeout(
        self,
        timeout_sec=2.0,
    ):

        self.node.get_logger().info(
            "Calling get_current_tcp service..."
        )

        # -----------------------------------------------------
        # 1. Wait for service
        # -----------------------------------------------------

        if not self.tcp_client.wait_for_service(
            timeout_sec=timeout_sec
        ):

            raise RobotConfigurationError(
                "get_current_tcp service unavailable "
                f"after {timeout_sec:.1f} sec"
            )

        # -----------------------------------------------------
        # 2. Send request
        # -----------------------------------------------------

        request = GetCurrentTcp.Request()

        future = self.tcp_client.call_async(
            request
        )

        # -----------------------------------------------------
        # 3. Wait for response with timeout
        # -----------------------------------------------------

        rclpy.spin_until_future_complete(
            self.node,
            future,
            timeout_sec=timeout_sec,
        )

        # -----------------------------------------------------
        # 4. Timeout
        # -----------------------------------------------------

        if not future.done():

            future.cancel()

            raise RobotConfigurationError(
                "get_current_tcp timeout "
                f"after {timeout_sec:.1f} sec"
            )

        # -----------------------------------------------------
        # 5. ROS service exception
        # -----------------------------------------------------

        exception = future.exception()

        if exception is not None:

            raise RobotConfigurationError(
                "get_current_tcp service error: "
                f"{exception}"
            )

        # -----------------------------------------------------
        # 6. Get response
        # -----------------------------------------------------

        response = future.result()

        if response is None:

            raise RobotConfigurationError(
                "get_current_tcp returned no response"
            )

        # -----------------------------------------------------
        # 7. Controller returned failure
        # -----------------------------------------------------

        if not response.success:

            raise RobotConfigurationError(
                "get_current_tcp service returned success=False"
            )

        tcp = response.info

        # -----------------------------------------------------
        # 8. Validate value
        # -----------------------------------------------------

        if not isinstance(tcp, str) or not tcp.strip():

            raise RobotConfigurationError(
                "Current TCP is empty"
            )

        self.node.get_logger().info(
            f"Current TCP = {tcp}"
        )

        return tcp


    # =========================================================
    # VALIDATE TOOL / TCP
    # =========================================================

    def validate_configuration(
        self,
        expected_tool=None,
        expected_tcp=None,
        timeout_sec=2.0,
    ):

        self.node.get_logger().info(
            "=========================================="
        )

        self.node.get_logger().info(
            "Validating robot Tool / TCP configuration"
        )

        # =====================================================
        # 1. TOOL
        # =====================================================

        tool = self.get_tool_with_timeout(
            timeout_sec=timeout_sec
        )

        # =====================================================
        # 2. TCP
        # =====================================================

        tcp = self.get_tcp_with_timeout(
            timeout_sec=timeout_sec
        )

        # =====================================================
        # 3. EXPECTED TOOL
        # =====================================================

        if expected_tool is not None:

            if tool != expected_tool:

                raise RobotConfigurationError(
                    "Wrong Tool: "
                    f"expected={expected_tool}, "
                    f"actual={tool}"
                )

        # =====================================================
        # 4. EXPECTED TCP
        # =====================================================

        if expected_tcp is not None:

            if tcp != expected_tcp:

                raise RobotConfigurationError(
                    "Wrong TCP: "
                    f"expected={expected_tcp}, "
                    f"actual={tcp}"
                )

        # =====================================================
        # 5. OK
        # =====================================================

        self.node.get_logger().info(
            "Robot configuration OK"
        )

        self.node.get_logger().info(
            f"Tool = {tool}"
        )

        self.node.get_logger().info(
            f"TCP  = {tcp}"
        )

        self.node.get_logger().info(
            "=========================================="
        )

        return tool, tcp


    # =========================================================
    # QUICK STOP
    # =========================================================

    def quick_stop(
        self,
        timeout_sec=1.0,
    ):

        self.node.get_logger().error(
            "ROBOT QUICK STOP REQUESTED"
        )

        # -----------------------------------------------------
        # 1. Check service
        # -----------------------------------------------------

        if not self.stop_client.wait_for_service(
            timeout_sec=timeout_sec
        ):

            raise RuntimeError(
                "MoveStop service unavailable "
                f"after {timeout_sec:.1f} sec"
            )

        # -----------------------------------------------------
        # 2. Request
        # -----------------------------------------------------

        request = MoveStop.Request()

        request.stop_mode = self.DR_QSTOP

        # -----------------------------------------------------
        # 3. Send
        # -----------------------------------------------------

        future = self.stop_client.call_async(
            request
        )

        self.node.get_logger().error(
            "Quick stop request sent"
        )

        return future