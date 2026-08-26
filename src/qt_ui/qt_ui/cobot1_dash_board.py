"""HMI main window for the toilet cleaning robot."""

import os

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer, pyqtSignal

from ament_index_python.packages import get_package_share_directory

from toilet_cleaning_interfaces.msg import CleaningStatus

from .manager_process import ManagerProcess


# Colour per cleaning state, used for the big state label.
STATE_COLOR = {
    CleaningStatus.IDLE: "#7f8c8d",
    CleaningStatus.DETECT_LID: "#3498db",
    CleaningStatus.OPEN_LID: "#3498db",
    CleaningStatus.APPLY_BLEACH: "#3498db",
    CleaningStatus.BRUSH_CLEAN: "#3498db",
    CleaningStatus.RINSE: "#3498db",
    CleaningStatus.FINISH: "#3498db",
    CleaningStatus.DONE: "#27ae60",
    CleaningStatus.ERROR: "#e74c3c",
}

# Korean label per cleaning state, shown next to the progress bar.
STATE_TEXT = {
    CleaningStatus.IDLE: "대기중",
    CleaningStatus.DETECT_LID: "뚜껑 감지중",
    CleaningStatus.OPEN_LID: "뚜껑 여는중",
    CleaningStatus.APPLY_BLEACH: "세정제 도포중",
    CleaningStatus.BRUSH_CLEAN: "솔 청소중",
    CleaningStatus.RINSE: "헹구는중",
    CleaningStatus.FINISH: "마무리중",
    CleaningStatus.DONE: "청소 완료",
    CleaningStatus.ERROR: "오류",
}

# How often the manager subprocess is checked for exit.
PROCESS_POLL_MS = 500


# =============================================================
# ROBOT GUI
# =============================================================

class RobotGUI(QtWidgets.QMainWindow):

    # ROS callbacks arrive on the executor thread. These signals hand the
    # data to the Qt thread, which is the only thread allowed to touch widgets.
    status_received = pyqtSignal(object)
    log_received = pyqtSignal(str)

    def __init__(self, ros2_node):

        super().__init__()

        # =====================================================
        # UI
        # =====================================================

        package_share_directory = get_package_share_directory("qt_ui")

        ui_file = os.path.join(
            package_share_directory,
            "cobot1_dash_board.ui"
        )

        uic.loadUi(ui_file, self)

        self.node = ros2_node

        self.node.set_gui(self)

        self.manager = ManagerProcess(
            log=self.log_received.emit
        )

        # =====================================================
        # Cross-thread signals
        # =====================================================

        self.status_received.connect(self.update_cleaning_status)

        self.log_received.connect(self.write_log)

        # =====================================================
        # Button
        # =====================================================

        self.btn_start.released.connect(self.start_cleaning)

        self.btn_stop.released.connect(self.stop_cleaning)

        self.btn_shutdown.released.connect(self.shutdown_robot)

        self.btn_estop.released.connect(self.emergency_stop)

        # =====================================================
        # Manager process watchdog
        # =====================================================

        self.process_timer = QTimer(self)

        self.process_timer.timeout.connect(self.check_manager_process)

        self.process_timer.start(PROCESS_POLL_MS)

        self.update_button_state()

        self.write_log("HMI ready. Press 시작 to run the cleaning sequence.")

    # =========================================================
    # Start Cleaning
    #
    # cleaning_manager begins the sequence as soon as it comes
    # up, so starting the process is the start command.
    # =========================================================

    def start_cleaning(self):

        if self.manager.is_running():

            self.write_log("청소가 이미 진행중입니다")

            return

        self.write_log("========== START CLEANING ==========")

        if self.manager.start():

            self.progress_bar.setValue(0)

            self.label_message.setText("cleaning_manager 기동중...")

        self.update_button_state()

    # =========================================================
    # Stop Cleaning
    # =========================================================

    def stop_cleaning(self):

        if not self.manager.is_running():

            self.write_log("진행중인 청소가 없습니다")

            return

        self.write_log("========== STOP CLEANING ==========")

        self.manager.stop()

        self.set_state_display(
            "STOPPED",
            "#f39c12",
            "사용자 정지"
        )

        self.update_button_state()

    # =========================================================
    # Emergency Stop
    # =========================================================

    def emergency_stop(self):

        self.write_log("========== EMERGENCY STOP ==========")

        # Halt the arm first, then kill the sequence that commands it.
        self.node.request_move_stop()

        if self.manager.is_running():

            self.manager.stop(force=True)

        self.set_state_display(
            "E-STOP",
            "#e74c3c",
            "긴급정지"
        )

        self.update_button_state()

    # =========================================================
    # Shutdown
    # =========================================================

    def shutdown_robot(self):

        self.close()

    # =========================================================
    # Manager Process Watchdog
    # =========================================================

    def check_manager_process(self):

        code = self.manager.poll_exit_code()

        if code is None:

            return

        if code == 0:

            self.write_log("cleaning_manager exited normally")

        else:

            self.write_log(
                f"cleaning_manager exited with code {code}"
            )

        self.update_button_state()

    # =========================================================
    # Cleaning Status
    #
    # Called from the ROS executor thread.
    # =========================================================

    def on_cleaning_status(self, msg):

        self.status_received.emit(msg)

    # =========================================================
    # Cleaning Status (Qt thread)
    # =========================================================

    def update_cleaning_status(self, msg):

        self.set_state_display(
            msg.state_name,
            STATE_COLOR.get(msg.state, "#2c3e50"),
            STATE_TEXT.get(msg.state, "-")
        )

        progress = max(0.0, min(1.0, float(msg.progress)))

        self.progress_bar.setValue(int(round(progress * 100.0)))

        if msg.message:

            self.label_message.setText(msg.message)

            self.write_log(
                f"[{msg.state_name}] {msg.message}"
            )

        else:

            self.label_message.setText("-")

            self.write_log(
                f"[{msg.state_name}]"
            )

    # =========================================================
    # State Display
    # =========================================================

    def set_state_display(self, state_name, color, running_text):

        self.label_state.setText(state_name)

        self.label_state.setStyleSheet(
            f"color: {color};"
        )

        self.label_running.setText(running_text)

    # =========================================================
    # Button State
    # =========================================================

    def update_button_state(self):

        running = self.manager.is_running()

        self.btn_start.setEnabled(not running)

        self.btn_stop.setEnabled(running)

    # =========================================================
    # System Log
    # =========================================================

    def write_log(self, text):

        self.text_log.append(str(text))

    # =========================================================
    # Close
    # =========================================================

    def closeEvent(self, event):

        self.process_timer.stop()

        if self.manager.is_running():

            self.manager.stop()

        self.node.shutdown()

        event.accept()
