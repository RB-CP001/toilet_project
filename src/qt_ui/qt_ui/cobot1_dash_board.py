"""HMI main window for the toilet cleaning robot."""

import os

from functools import partial

from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer, pyqtSignal

from ament_index_python.packages import get_package_share_directory

from toilet_cleaning_interfaces.msg import CleaningStatus

from .robot_process import RobotProcess


# Full sequence: cleaning_manager drives every step and publishes status.
FULL_RUN = ("cleaning_manager", "전체 청소")

# Individual steps. Each toilet_cleaning node runs one step through its own
# main() -> run(), the same way cleaning_manager is launched.
#
#   (버튼 이름, executable, 표시 이름, 뚜껑이 열려 있어야 하는가)
STEP_BUTTONS = [
    ("btn_open_lid",     "open_lid",     "뚜껑 열기",        False),
    ("btn_apply_bleach", "apply_bleach", "세제 도포",        True),
    ("btn_brush_clean",  "brush_clean",  "변기 솔질",        True),
    ("btn_rinse",        "rinse",        "변기 세척",        True),
    ("btn_finish",       "finish",       "뚜껑 닫고 물내림", False),
]

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

# Flavour line shown next to the state name. Keyed by cleaning state so the
# full sequence and a single step share one table.
STATE_FLAVOR = {
    CleaningStatus.IDLE: "성역은 고요하다...",
    CleaningStatus.DETECT_LID: "변좌의 상태를 확인하는 중이다...",
    CleaningStatus.OPEN_LID: "변좌가... 더럽혀졌군...",
    CleaningStatus.APPLY_BLEACH: "정화를 시작한다!!",
    CleaningStatus.BRUSH_CLEAN: "오물에게 자비란 없다!! 내 솔을 받아라!!",
    CleaningStatus.RINSE: "백색의 변좌에 다시 광명을...!",
    CleaningStatus.FINISH: "정화 완료. 성역은 다시 평화를 되찾았다..",
    CleaningStatus.DONE: "모든 의식이 끝났다. 성역은 빛난다.",
    CleaningStatus.ERROR: "의식이 중단되었다... 무언가 잘못되었다.",
}

# Which cleaning state each standalone node corresponds to, so a single step
# can reuse STATE_FLAVOR above.
STEP_STATE = {
    "detect_lid": CleaningStatus.DETECT_LID,
    "open_lid": CleaningStatus.OPEN_LID,
    "apply_bleach": CleaningStatus.APPLY_BLEACH,
    "brush_clean": CleaningStatus.BRUSH_CLEAN,
    "rinse": CleaningStatus.RINSE,
    "finish": CleaningStatus.FINISH,
}

# How often the robot subprocess is checked for exit.
PROCESS_POLL_MS = 500


# =============================================================
# ROBOT GUI
# =============================================================

class RobotGUI(QtWidgets.QMainWindow):

    # ROS callbacks and the subprocess reader both run off the Qt thread.
    # These signals hand their data to the Qt thread, which is the only
    # thread allowed to touch widgets.
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

        # =====================================================
        # Cross-thread signals
        # =====================================================

        self.status_received.connect(self.update_cleaning_status)

        self.log_received.connect(self.write_log)

        self.node.set_callbacks(
            on_status=self.status_received.emit,
            on_log=self.log_received.emit,
        )

        # =====================================================
        # Robot process
        # =====================================================

        self.proc = RobotProcess(
            log=self.log_received.emit,
            output=self.log_received.emit,
        )

        # True while the full sequence runs, so status messages from
        # cleaning_manager are only trusted then.
        self.full_run = False

        # Set when the user killed the run, so the watchdog reports a stop
        # instead of a crash.
        self.aborted = False

        # =====================================================
        # Control buttons
        # =====================================================

        self.btn_start.released.connect(self.start_full_run)

        self.btn_shutdown.released.connect(self.shutdown_robot)

        self.btn_estop.released.connect(self.emergency_stop)

        # =====================================================
        # Step buttons
        # =====================================================

        self.run_buttons = [self.btn_start]

        for name, executable, label, needs_open_lid in STEP_BUTTONS:

            button = getattr(self, name)

            # partial, not lambda: a lambda in this loop would capture the
            # loop variable by reference and every button would run the last step.
            button.released.connect(
                partial(self.run_step, executable, label, needs_open_lid)
            )

            self.run_buttons.append(button)

        # =====================================================
        # Process watchdog
        # =====================================================

        self.process_timer = QTimer(self)

        self.process_timer.timeout.connect(self.check_process)

        self.process_timer.start(PROCESS_POLL_MS)

        self.update_button_state()

        self.write_log("HMI ready. 전체 청소 또는 개별 공정을 선택하세요.")

    # =========================================================
    # Full Sequence
    #
    # cleaning_manager begins the sequence as soon as it comes
    # up, so starting the process is the start command.
    # =========================================================

    def start_full_run(self):

        if self.proc.is_running():

            return

        self.aborted = False

        executable, label = FULL_RUN

        self.write_log(f"========== {label} 시작 ==========")

        if not self.proc.start(executable, label):

            return

        self.full_run = True

        self.progress_bar.setRange(0, 100)

        self.progress_bar.setValue(0)

        self.set_state_display(
            "STARTING",
            "#3498db",
            label,
            "정화 의식을 시작한다..."
        )

        self.label_message.setText("cleaning_manager 기동중...")

        self.update_button_state()

    # =========================================================
    # Single Step
    #
    # Each step node runs the same way as cleaning_manager:
    # main() -> setup_doosan() -> import DSR_ROBOT2 -> run().
    # =========================================================

    def run_step(self, executable, label, needs_open_lid):

        if self.proc.is_running():

            return

        self.aborted = False

        # Steps are self-contained but not order-checked. Running a bowl
        # step with the lid down would drive the tool into the lid.
        if needs_open_lid and not self.confirm_lid_open(label):

            return

        self.write_log(f"========== {label} 시작 ==========")

        if not self.proc.start(executable, label):

            return

        self.full_run = False

        # Step nodes publish no status, so there is no progress to show.
        # An indeterminate bar signals "running" without faking a number.
        self.progress_bar.setRange(0, 0)

        self.set_state_display(
            executable.upper(),
            "#16a085",
            f"{label} 실행 중",
            STATE_FLAVOR.get(STEP_STATE.get(executable), "-")
        )

        self.label_message.setText(f"{label} 단독 실행 중입니다.")

        self.update_button_state()

    # =========================================================
    # Lid Confirmation
    # =========================================================

    def confirm_lid_open(self, label):

        answer = QtWidgets.QMessageBox.question(
            self,
            "실행 확인",
            f"[{label}]을(를) 단독 실행합니다.\n\n"
            "변기 뚜껑이 열려 있습니까?\n"
            "닫힌 상태로 실행하면 도구가 뚜껑에 충돌합니다.",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No,
        )

        if answer != QtWidgets.QMessageBox.Yes:

            self.write_log(f"{label} 실행 취소됨")

            return False

        return True

    # =========================================================
    # Emergency Stop
    # =========================================================

    def emergency_stop(self):

        self.write_log("========== EMERGENCY STOP ==========")

        # Halt the arm first, then kill whatever is commanding it.
        self.node.request_move_stop()

        self.aborted = True

        self.proc.stop(force=True)

        self.full_run = False

        self.progress_bar.setRange(0, 100)

        self.set_state_display(
            "E-STOP",
            "#e74c3c",
            "긴급정지",
            "의식이 강제로 중단되었다!"
        )

        self.label_message.setText("긴급정지 되었습니다.")

        self.update_button_state()

    # =========================================================
    # Shutdown
    # =========================================================

    def shutdown_robot(self):

        self.close()

    # =========================================================
    # Process Watchdog
    # =========================================================

    def check_process(self):

        code = self.proc.poll_exit_code()

        if code is None:

            return

        label = self.proc.label or "프로세스"

        # A kill the user asked for is not a crash.
        if self.aborted:

            self.write_log(f"{label} 긴급정지로 중단됨")

        # Step nodes log their failures and still exit 0, so the captured
        # output is what decides success.
        elif self.proc.saw_error:

            self.write_log(f"{label} 실패 (로그 확인)")

            self.set_state_display(
                "ERROR",
                "#e74c3c",
                "오류",
                STATE_FLAVOR[CleaningStatus.ERROR]
            )

        elif code == 0:

            self.write_log(f"{label} 완료")

            if not self.full_run:

                self.set_state_display(
                    "DONE",
                    "#27ae60",
                    f"{label} 완료",
                    STATE_FLAVOR[CleaningStatus.DONE]
                )

        else:

            self.write_log(f"{label} 비정상 종료 (code {code})")

            self.set_state_display(
                "ERROR",
                "#e74c3c",
                "비정상 종료",
                STATE_FLAVOR[CleaningStatus.ERROR]
            )

        self.full_run = False

        self.progress_bar.setRange(0, 100)

        self.update_button_state()

    # =========================================================
    # Cleaning Status (Qt thread)
    # =========================================================

    def update_cleaning_status(self, msg):

        # Only cleaning_manager publishes this. Ignore it while a single
        # step runs, so a retained message cannot overwrite the step display.
        if not self.full_run:

            return

        self.set_state_display(
            msg.state_name,
            STATE_COLOR.get(msg.state, "#2c3e50"),
            STATE_TEXT.get(msg.state, "-"),
            STATE_FLAVOR.get(msg.state, "-")
        )

        progress = max(0.0, min(1.0, float(msg.progress)))

        self.progress_bar.setValue(int(round(progress * 100.0)))

        if msg.message:

            self.label_message.setText(msg.message)

            self.write_log(f"[{msg.state_name}] {msg.message}")

        else:

            self.label_message.setText("-")

            self.write_log(f"[{msg.state_name}]")

    # =========================================================
    # State Display
    # =========================================================

    def set_state_display(self, state_name, color, running_text, flavor=None):

        self.label_state.setText(state_name)

        self.label_state.setStyleSheet(f"color: {color};")

        self.label_running.setText(running_text)

        if flavor is not None:

            self.label_flavor.setText(flavor)

    # =========================================================
    # Button State
    # =========================================================

    def update_button_state(self):

        running = self.proc.is_running()

        # One robot process at a time. Emergency stop stays live.
        for button in self.run_buttons:

            button.setEnabled(not running)

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

        self.proc.stop_and_wait()

        self.node.shutdown()

        event.accept()
