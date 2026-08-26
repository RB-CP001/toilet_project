"""
dashboard_node.py — 변기 청소 로봇 대시보드 (ROS2 노드)

  대시보드  ──/tcr/command──▶  cleaning_manager  ──▶  각 스텝 노드
            ◀─/tcr/status────
            ◀─/tcr/log───────

실행:  ros2 run toilet_cleaning dashboard

────────────────────────────────────────────────────────────
왜 스레드를 안 쓰는가

rclpy와 Qt는 각자 자기만의 이벤트 루프를 돌린다. 보통 rclpy를 별도
스레드에서 spin 시키는데, 그러면 콜백이 다른 스레드에서 실행되므로
Qt 위젯을 직접 건드릴 수 없다(Qt는 GUI 스레드에서만 위젯 조작을 허용한다).

여기서는 Qt의 이벤트 루프를 주인으로 두고, QTimer로 10ms마다
rclpy.spin_once(timeout_sec=0)를 호출한다. 모든 것이 한 스레드에서
돌아가므로 락도, 시그널 중계도 필요 없다.

GUI처럼 처리량이 적은 노드에는 이 방식이 가장 단순하고 안전하다.
────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

import rclpy
from ament_index_python.packages import get_package_share_directory
from rclpy.node import Node
from std_msgs.msg import String

from PyQt5 import uic
from PyQt5.QtCore import Qt, QTime, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication, QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget,
)

from toilet_cleaning.tcr_widgets import C, ClickableCard, F, mix


# ════════════════════════════════════════════════════════════
# 청소 공정 — cleaning_manager 쪽 순서와 반드시 일치해야 한다
# ════════════════════════════════════════════════════════════
@dataclass(frozen=True)
class Step:
    id: int
    ko: str
    en: str


STEPS: list[Step] = [
    Step(1, "뚜껑 열기",             "Open Lid"),
    Step(2, "세제 도포",             "Apply Bleach"),
    Step(3, "브러시 청소",           "Brush Clean"),
    Step(4, "물 뿌리기",             "Rinse"),
    Step(5, "뚜껑 닫고 레버 누르기", "Finish"),
]

# 매니저에서 status 메시지가 이 시간 넘게 안 오면 연결 이상으로 본다
WAIT_AFTER_MS = 2000     # 대기 중
ERROR_AFTER_MS = 5000    # 연결 오류

STATUS_INFO = {
    "idle":      (C.MUTED, "STANDBY",  "READY"),
    "running":   (C.BLUE,  "RUNNING",  "NOW RUNNING"),
    "paused":    (C.AMBER, "PAUSED",   "PAUSED AT"),
    "homing":    (C.BLUE,  "HOMING",   "RETURNING HOME"),
    "emergency": (C.RED,   "E-STOP",   "STOPPED AT"),
    "complete":  (C.GREEN, "COMPLETE", "FINISHED"),
}

CONN_INFO = {
    "online": (C.GREEN, "정상 연결", "매니저 연결됨 — /tcr/status 수신 중"),
    "wait":   (C.AMBER, "대기 중",   "매니저 응답 없음 — 재연결 대기"),
    "error":  (C.RED,   "연결 오류", "통신 두절 — cleaning_manager 확인 필요"),
}


# ════════════════════════════════════════════════════════════
# 단일 청소 다이얼로그
# ════════════════════════════════════════════════════════════
class SingleCleanDialog(QDialog):
    """실행할 공정을 하나 고르는 팝업."""

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.selected_index: int | None = None

        self.setWindowTitle("단일 청소")
        self.setModal(True)
        self.setFixedWidth(360)
        self.setStyleSheet(f"QDialog {{ background:{C.L2}; }}")

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 22, 24, 22)
        root.setSpacing(0)

        title = QLabel("단일 청소")
        title.setFont(F.ui(13, QFont.Bold))
        title.setStyleSheet(f"color:{C.TX};")
        root.addWidget(title)

        desc = QLabel("실행할 단계를 선택하면 해당 스텝만 진행합니다.")
        desc.setFont(F.ui(9))
        desc.setStyleSheet(f"color:{C.SUB};")
        root.addWidget(desc)
        root.addSpacing(16)

        for i, step in enumerate(STEPS):
            root.addWidget(self._make_option(i, step))
            root.addSpacing(7)

        root.addSpacing(5)
        cancel = QPushButton("취소")
        cancel.setFixedHeight(40)
        cancel.setCursor(Qt.PointingHandCursor)
        cancel.setFont(F.ui(10))
        cancel.setStyleSheet(f"""
            QPushButton {{
                background:transparent; color:{C.SUB};
                border:1px solid {C.BORDER}; border-radius:10px;
            }}
            QPushButton:hover {{ color:{C.TX}; border-color:{C.BORDER2}; }}
        """)
        cancel.clicked.connect(self.reject)
        root.addWidget(cancel)

    def _make_option(self, index: int, step: Step) -> QWidget:
        card = ClickableCard()
        card.setFixedHeight(56)
        card.set_colors(C.L3, mix(C.BLUE, C.L3, 0.10), C.BORDER, C.BLUE)
        card.clicked.connect(lambda: self._choose(index))

        row = QHBoxLayout(card)
        row.setContentsMargins(14, 0, 14, 0)
        row.setSpacing(13)

        num = QLabel(f"{step.id:02d}")
        num.setFixedSize(32, 32)
        num.setAlignment(Qt.AlignCenter)
        num.setFont(F.mono(10, QFont.Bold))
        num.setStyleSheet(
            f"background:{mix(C.BLUE, C.L3, 0.16)}; color:{C.BLUE}; border-radius:8px;"
        )
        row.addWidget(num)

        text = QVBoxLayout()
        text.setSpacing(0)
        ko = QLabel(step.ko)
        ko.setFont(F.ui(10, QFont.Bold))
        ko.setStyleSheet(f"color:{C.TX};")
        en = QLabel(step.en)
        en.setFont(F.ui(8))
        en.setStyleSheet(f"color:{C.SUB};")
        text.addWidget(ko)
        text.addWidget(en)
        row.addLayout(text)
        row.addStretch()

        return card

    def _choose(self, index: int) -> None:
        self.selected_index = index
        self.accept()


# ════════════════════════════════════════════════════════════
# 대시보드
# ════════════════════════════════════════════════════════════
class Dashboard(QWidget):
    """
    화면은 상태를 판단하지 않는다. 그리기만 한다.

    버튼을 누르면 /tcr/command 로 명령만 보내고, 화면은 /tcr/status 가
    올 때까지 바뀌지 않는다. 그래야 화면에 보이는 값이 항상 로봇의
    진짜 상태다. 화면에서 먼저 바꿔버리면, 매니저가 명령을 거부했을 때
    화면과 로봇이 서로 다른 말을 하게 된다.
    """

    def __init__(self, node: Node) -> None:
        super().__init__()
        self.node = node

        ui_path = Path(get_package_share_directory("toilet_cleaning")) / "ui" / "tcr_dashboard.ui"
        uic.loadUi(str(ui_path), self)

        # ── 상태 (전부 매니저가 내려주는 값) ────────────────
        self.status = "idle"
        self.step = 0
        self.percent = 0.0
        self.started = False
        self.single = False
        self.conn = "wait"          # 첫 status를 받기 전까지는 대기
        self.last_status_ms = 0

        self.chips = [self.chip1, self.chip2, self.chip3, self.chip4, self.chip5]

        # ── ROS2 통신 ─────────────────────────────────────
        self.pub_command = node.create_publisher(String, "/tcr/command", 10)
        node.create_subscription(String, "/tcr/status", self._on_status, 10)
        node.create_subscription(String, "/tcr/log", self._on_log, 50)

        self._setup_fonts()
        self._setup_steps()
        self._setup_signals()
        self._setup_timers()

        self.log("대시보드 시작 — cleaning_manager 연결 대기 중")
        self.refresh()

    # ────────────────────────────────────────────────────
    # 초기 설정
    # ────────────────────────────────────────────────────
    def _setup_fonts(self) -> None:
        self.lblTitle.setFont(F.ui(11, QFont.Bold))
        self.lblUnit.setFont(F.mono(8, spacing=0.8))
        self.btnConn.setFont(F.ui(9, QFont.DemiBold))
        self.lblStatus.setFont(F.mono(9, QFont.DemiBold, 0.6))
        self.lblClock.setFont(F.mono(9))

        self.lblEyebrow.setFont(F.mono(8, spacing=1.0))
        self.lblTitleKo.setFont(F.ui(22, QFont.Bold))
        self.lblTitleEn.setFont(F.ui(10))
        self.lblTotalCaption.setFont(F.mono(8, spacing=0.8))
        self.lblTotalValue.setFont(F.mono(9, QFont.DemiBold))

        self.lblStopText.setFont(F.ui(11, QFont.Bold))
        self.lblLogCaption.setFont(F.mono(8, QFont.DemiBold, 0.9))
        self.lblLive.setFont(F.mono(7, spacing=0.8))

        for ko, en in ((self.lblSingleKo, self.lblSingleEn),
                       (self.lblHomeKo, self.lblHomeEn),
                       (self.lblResetKo, self.lblResetEn)):
            ko.setFont(F.ui(11, QFont.Bold))
            en.setFont(F.mono(7, QFont.DemiBold, 1.2))

        self.cardStop.set_colors(
            C.L1, mix(C.RED, C.L1, 0.10),
            mix(C.RED, C.L1, 0.28), mix(C.RED, C.L1, 0.60),
        )
        # 부모 카드가 자식 QLabel 배경을 투명으로 만들기 때문에 직접 지정한다
        self.lblKnob.setStyleSheet(f"background:{C.RED}; border:none; border-radius:13px;")

    def _setup_steps(self) -> None:
        for chip, step in zip(self.chips, STEPS):
            chip.set_step(step.id, step.ko)

    def _setup_signals(self) -> None:
        self.btnMain.clicked.connect(self.on_main)
        self.cardStop.clicked.connect(lambda: self.send("estop"))
        self.cardSingle.clicked.connect(self.on_single)
        self.cardHome.clicked.connect(lambda: self.send("home"))
        self.cardReset.clicked.connect(lambda: self.send("reset"))
        self.btnConn.clicked.connect(self._report_conn)

    def _setup_timers(self) -> None:
        # ── rclpy를 Qt 이벤트 루프에 얹는다 ────────────────
        self.ros_timer = QTimer(self)
        self.ros_timer.setInterval(10)
        self.ros_timer.timeout.connect(self._spin_once)
        self.ros_timer.start()

        # 매니저 응답 감시
        self.watchdog = QTimer(self)
        self.watchdog.setInterval(500)
        self.watchdog.timeout.connect(self._check_connection)
        self.watchdog.start()

        self.clock_timer = QTimer(self)
        self.clock_timer.setInterval(1000)
        self.clock_timer.timeout.connect(self._update_clock)
        self.clock_timer.start()
        self._update_clock()

    def _spin_once(self) -> None:
        """콜백을 한 번씩 비워준다. timeout_sec=0이라 블로킹되지 않는다."""
        rclpy.spin_once(self.node, timeout_sec=0)

    # ────────────────────────────────────────────────────
    # ROS2 — 보내기
    # ────────────────────────────────────────────────────
    def send(self, cmd: str, **extra) -> None:
        payload = {"cmd": cmd, **extra}
        self.pub_command.publish(String(data=json.dumps(payload)))
        self.node.get_logger().info(f"command → {payload}")

    def on_main(self) -> None:
        if self.status == "running":
            self.send("pause")
        elif self.status == "paused":
            self.send("resume")
        else:
            self.send("start")

    def on_single(self) -> None:
        dialog = SingleCleanDialog(self)
        if dialog.exec_() == QDialog.Accepted and dialog.selected_index is not None:
            self.send("single", step=dialog.selected_index)

    # ────────────────────────────────────────────────────
    # ROS2 — 받기
    # ────────────────────────────────────────────────────
    def _on_status(self, msg: String) -> None:
        try:
            data = json.loads(msg.data)
        except json.JSONDecodeError:
            self.log("status 파싱 실패 — JSON 형식 확인", "err")
            return

        self.status = data.get("status", self.status)
        self.step = int(data.get("step", self.step))
        self.percent = float(data.get("pct", self.percent))
        self.started = bool(data.get("started", self.started))
        self.single = bool(data.get("single", self.single))

        self.last_status_ms = QTime.currentTime().msecsSinceStartOfDay()
        if self.conn != "online":
            self._set_conn("online")
        self.refresh()

    def _on_log(self, msg: String) -> None:
        try:
            data = json.loads(msg.data)
            self.log(data.get("msg", ""), data.get("level", "info"))
        except json.JSONDecodeError:
            self.log(msg.data)      # 그냥 문자열로 보냈어도 받아준다

    def _check_connection(self) -> None:
        if self.last_status_ms == 0:
            return                  # 아직 한 번도 못 받음 — 초기 wait 유지
        elapsed = QTime.currentTime().msecsSinceStartOfDay() - self.last_status_ms
        if elapsed > ERROR_AFTER_MS:
            self._set_conn("error")
        elif elapsed > WAIT_AFTER_MS:
            self._set_conn("wait")

    def _set_conn(self, state: str) -> None:
        if state == self.conn:
            return
        self.conn = state
        _, _, message = CONN_INFO[state]
        self.log(message, {"online": "ok", "wait": "warn", "error": "err"}[state])
        self.refresh()

    def _report_conn(self) -> None:
        """표시등을 누르면 현재 상태를 로그에 남긴다."""
        _, _, message = CONN_INFO[self.conn]
        self.log(message, "info")

    # ────────────────────────────────────────────────────
    # 로그
    # ────────────────────────────────────────────────────
    def log(self, message: str, level: str = "info") -> None:
        color = {"info": C.SUB, "ok": C.GREEN, "warn": C.AMBER, "err": C.RED}.get(level, C.SUB)
        stamp = QTime.currentTime().toString("HH:mm:ss")
        self.txtLog.append(
            f'<span style="font-family:{F.MONO}; font-size:11px;">'
            f'<span style="color:{C.MUTED};">{stamp}</span>'
            f'&nbsp;&nbsp;&nbsp;<span style="color:{color};">{message}</span></span>'
        )
        bar = self.txtLog.verticalScrollBar()
        bar.setValue(bar.maximum())

    # ────────────────────────────────────────────────────
    # 화면 갱신
    # ────────────────────────────────────────────────────
    def total_percent(self) -> float:
        if self.status == "complete":
            return 100.0
        if not self.started:
            return 0.0
        if self.single:
            return self.percent
        return (self.step + self.percent / 100) / len(STEPS) * 100

    def refresh(self) -> None:
        accent, pill_text, eyebrow = STATUS_INFO.get(self.status, STATUS_INFO["idle"])
        active_now = self.status in ("running", "paused", "homing", "emergency")

        self.lblStatus.setText(f"  {pill_text}  ")
        self.lblStatus.setStyleSheet(
            f"color:{accent}; background:{mix(accent, C.L1, 0.10)};"
            f"border:1px solid {mix(accent, C.L1, 0.24)}; border-radius:13px; padding:0 10px;"
        )
        self._refresh_conn_button()

        if self.status == "complete":
            big = "✓"
        elif self.status == "emergency":
            big = "!"
        elif self.started and active_now:
            big = f"{STEPS[self.step].id:02d}"
        else:
            big = "—"

        show_pct = self.started and self.status in ("running", "paused", "homing")
        self.ring.update_view(
            percent=self.percent if self.started else 0.0,
            color=accent,
            caption="STEP" if self.started else "STATUS",
            big=big,
            small=f"{self.percent:.0f}%" if show_pct else "",
        )

        self.lblEyebrow.setText(eyebrow)
        if self.status == "homing":
            ko, en = "홈 복귀 중", "Returning to home position"
        elif self.status == "idle":
            ko, en = "대기중", "Start cleaning to begin"
        elif self.status == "complete":
            ko, en = "청소 완료", "All steps finished successfully"
        elif self.status == "emergency":
            ko, en = "비상 정지", "Reset to continue"
        else:
            ko, en = STEPS[self.step].ko, STEPS[self.step].en
        self.lblTitleKo.setText(ko)
        self.lblTitleEn.setText(en)

        total = self.total_percent()
        self.lblTotalValue.setText(f"{total:.0f}%")
        self.barTotal.update_view(total, accent if self.status != "idle" else C.BLUE)

        for i, chip in enumerate(self.chips):
            if self.status == "complete" and not self.single:
                state = "done"
            elif not self.single and self.started and i < self.step:
                state = "done"
            elif i == self.step and active_now:
                state = "active"
            else:
                state = "pending"
            chip.update_view(state, self.percent, accent)

        self._refresh_main_button(accent)

    def _refresh_main_button(self, accent: str) -> None:
        if self.status == "running":
            icon, text = "❚❚", "일시정지"
        elif self.status == "paused":
            icon, text = "▶", "재 개"
        elif self.status == "complete":
            icon, text = "↺", "재시작"
        elif self.status == "homing":
            icon, text = "⌂", "홈 복귀 중…"
        else:
            icon, text = "▶", "청소 시작 진행"

        # 비상정지 중이거나 통신이 끊겼으면 시작을 막는다
        disabled = self.status in ("emergency", "homing") or self.conn == "error"
        self.btnMain.setEnabled(not disabled)
        self.btnMain.setText(f"{icon}\n\n{text}")

        if disabled:
            self.btnMain.setStyleSheet(f"""
                QPushButton {{
                    background:{C.L1}; color:{C.MUTED};
                    border:1px solid {C.BORDER}; border-radius:16px;
                }}
            """)
        else:
            self.btnMain.setStyleSheet(f"""
                QPushButton {{
                    background:{mix(accent, C.L1, 0.08)}; color:{accent};
                    border:1px solid {mix(accent, C.L1, 0.28)}; border-radius:16px;
                }}
                QPushButton:hover {{
                    background:{mix(accent, C.L1, 0.14)};
                    border-color:{mix(accent, C.L1, 0.55)};
                }}
            """)

    def _refresh_conn_button(self) -> None:
        color, label, _ = CONN_INFO[self.conn]
        self.btnConn.setText(f"  ● {label}  ")
        self.btnConn.setStyleSheet(f"""
            QPushButton {{
                color:{color}; background:{mix(color, C.L1, 0.09)};
                border:1px solid {mix(color, C.L1, 0.24)};
                border-radius:13px; padding:0 8px;
            }}
            QPushButton:hover {{ background:{mix(color, C.L1, 0.16)}; }}
        """)

    def _update_clock(self) -> None:
        self.lblClock.setText(QTime.currentTime().toString("HH:mm:ss"))

    # 단축키: Space = 시작/정지, Esc = 비상정지
    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Space and self.btnMain.isEnabled():
            self.on_main()
        elif event.key() == Qt.Key_Escape:
            self.send("estop")
        else:
            super().keyPressEvent(event)


def main(args=None) -> None:
    rclpy.init(args=args)
    node = rclpy.create_node("tcr_dashboard")

    app = QApplication(sys.argv)
    F.init()
    app.setFont(F.ui(10))

    window = Dashboard(node)
    window.show()

    try:
        exit_code = app.exec_()
    finally:
        node.destroy_node()
        rclpy.shutdown()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()