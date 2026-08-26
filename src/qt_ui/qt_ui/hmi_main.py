"""Entry point for the toilet cleaning HMI.

Qt owns the main thread; rclpy is spun on a background thread so the executor
never blocks the UI.
"""

import signal
import sys
import threading

import rclpy

from rclpy.executors import SingleThreadedExecutor

from PyQt5 import QtWidgets

from .cobot1_dash_board import RobotGUI
from .ros2_node import RobotNode


# =============================================================
# ROS SPIN THREAD
# =============================================================

class RosSpinner:

    def __init__(self, node):

        self.executor = SingleThreadedExecutor()

        self.executor.add_node(node)

        self.thread = threading.Thread(
            target=self._spin,
            daemon=True
        )

    def start(self):

        self.thread.start()

    def _spin(self):

        try:

            self.executor.spin()

        except Exception:

            # Raised when the executor is shut down from the Qt thread.
            pass

    def stop(self):

        self.executor.shutdown()

        self.thread.join(timeout=2.0)


# =============================================================
# MAIN
# =============================================================

def main(args=None):

    rclpy.init(args=args)

    node = RobotNode()

    spinner = RosSpinner(node)

    app = QtWidgets.QApplication(sys.argv)

    # Let Ctrl+C in the launching terminal close the window.
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    gui = RobotGUI(node)

    gui.show()

    spinner.start()

    try:

        exit_code = app.exec_()

    finally:

        spinner.stop()

        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()

    sys.exit(exit_code)


if __name__ == "__main__":

    main()
