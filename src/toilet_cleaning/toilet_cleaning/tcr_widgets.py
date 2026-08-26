"""
tcr_widgets.py — Qt Designer 승격(promote)용 커스텀 위젯

Qt Designer에는 원형 게이지 같은 위젯이 없다. 그래서 Designer에서는
빈 QWidget을 올려두고 "승격"으로 이 파일의 클래스를 지정한다.
Designer 화면에서는 빈 사각형으로 보이지만, 실행하면 진짜로 그려진다.

  승격 설정 (Designer에서 위젯 우클릭 → Promote to...)
    Base class name   : QWidget  (ClickableCard만 QFrame)
    Promoted class    : RingGauge / ProgressBar / StepChip / ClickableCard
    Header file       : tcr_widgets

모든 클래스는 parent만 받는 생성자를 갖는다. Designer가 그렇게 호출하기 때문이다.
"""

from __future__ import annotations

from PyQt5.QtCore import QRectF, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QFontDatabase, QPainter, QPen
from PyQt5.QtWidgets import QFrame, QWidget


# ════════════════════════════════════════════════════════════
# 색 · 폰트
# ════════════════════════════════════════════════════════════
class C:
    """색상 팔레트. Qt 스타일시트는 알파가 까다로워서 전부 불투명 값으로 둔다."""
    BG      = "#07090F"
    L1      = "#0C0F1A"
    L2      = "#111527"
    L3      = "#161B30"
    BORDER  = "#1B2032"
    BORDER2 = "#262C40"

    BLUE  = "#5880FF"
    GREEN = "#00D87A"
    RED   = "#FF4C5E"
    AMBER = "#FFA826"

    TX    = "#E8EAF0"
    SUB   = "#8A91A8"
    MUTED = "#3D445A"


def mix(fg: str, bg: str, ratio: float) -> str:
    """fg를 bg 위에 ratio(0~1)만큼 얹은 색. 반투명 대신 쓴다."""
    f, b = QColor(fg), QColor(bg)
    return QColor(
        round(b.red()   + (f.red()   - b.red())   * ratio),
        round(b.green() + (f.green() - b.green()) * ratio),
        round(b.blue()  + (f.blue()  - b.blue())  * ratio),
    ).name()


def _pick(candidates: list[str], fallback: str) -> str:
    available = set(QFontDatabase().families())
    for name in candidates:
        if name in available:
            return name
    return fallback


class F:
    """폰트 패밀리. QApplication 생성 후 F.init()을 한 번 부른다."""
    UI = "Sans Serif"
    MONO = "Monospace"

    @classmethod
    def init(cls) -> None:
        cls.UI = _pick(
            ["Pretendard", "Pretendard Variable", "Apple SD Gothic Neo",
             "Malgun Gothic", "NanumGothic", "Noto Sans CJK KR"],
            "Sans Serif",
        )
        cls.MONO = _pick(
            ["JetBrains Mono", "D2Coding", "Consolas", "DejaVu Sans Mono"],
            "Monospace",
        )

    @classmethod
    def ui(cls, size: int, weight: int = QFont.Normal, spacing: float = 0.0) -> QFont:
        f = QFont(cls.UI, size, weight)
        if spacing:
            f.setLetterSpacing(QFont.AbsoluteSpacing, spacing)
        return f

    @classmethod
    def mono(cls, size: int, weight: int = QFont.Normal, spacing: float = 0.0) -> QFont:
        f = QFont(cls.MONO, size, weight)
        if spacing:
            f.setLetterSpacing(QFont.AbsoluteSpacing, spacing)
        return f


# ════════════════════════════════════════════════════════════
# 원형 게이지
# ════════════════════════════════════════════════════════════
class RingGauge(QWidget):
    """현재 스텝의 진행률을 보여주는 원형 게이지."""

    THICKNESS = 10

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.percent = 0.0
        self.color = C.MUTED
        self.caption = "STATUS"   # 링 위쪽 작은 글씨
        self.big = "—"            # 가운데 큰 글씨
        self.small = ""           # 아래쪽 퍼센트

    def update_view(self, *, percent: float, color: str,
                    caption: str, big: str, small: str = "") -> None:
        self.percent, self.color = percent, color
        self.caption, self.big, self.small = caption, big, small
        self.update()

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        side = min(self.width(), self.height())
        pad = self.THICKNESS / 2 + 1
        left = (self.width() - side) / 2 + pad
        top = (self.height() - side) / 2 + pad
        box = QRectF(left, top, side - pad * 2, side - pad * 2)

        p.setPen(QPen(QColor(mix("#FFFFFF", C.L1, 0.06)), self.THICKNESS))
        p.drawArc(box, 0, 360 * 16)

        if self.percent > 0:                      # 12시 방향에서 시계 방향
            pen = QPen(QColor(self.color), self.THICKNESS)
            pen.setCapStyle(Qt.RoundCap)
            p.setPen(pen)
            p.drawArc(box, 90 * 16, int(-self.percent / 100 * 360 * 16))

        cy = self.height() / 2

        p.setPen(QColor(C.MUTED))
        p.setFont(F.mono(9, QFont.DemiBold, 1.2))
        p.drawText(QRectF(0, cy - 46, self.width(), 16), Qt.AlignCenter, self.caption)

        p.setPen(QColor(self.color))
        p.setFont(F.mono(38, QFont.Black))
        p.drawText(QRectF(0, cy - 30, self.width(), 62), Qt.AlignCenter, self.big)

        if self.small:
            p.setPen(QColor(self.color))
            p.setFont(F.mono(11, QFont.DemiBold))
            p.drawText(QRectF(0, cy + 32, self.width(), 18), Qt.AlignCenter, self.small)


# ════════════════════════════════════════════════════════════
# 진행 막대
# ════════════════════════════════════════════════════════════
class ProgressBar(QWidget):
    """전체 진행률 막대."""

    RADIUS = 3

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.percent = 0.0
        self.color = C.BLUE

    def update_view(self, percent: float, color: str) -> None:
        self.percent, self.color = percent, color
        self.update()

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)

        p.setBrush(QColor(C.L3))
        p.drawRoundedRect(QRectF(self.rect()), self.RADIUS, self.RADIUS)

        if self.percent > 0:
            w = self.width() * self.percent / 100
            p.setBrush(QColor(self.color))
            p.drawRoundedRect(QRectF(0, 0, w, self.height()), self.RADIUS, self.RADIUS)


# ════════════════════════════════════════════════════════════
# 스텝 칩
# ════════════════════════════════════════════════════════════
class StepChip(QWidget):
    """
    스텝 하나를 나타내는 칩. 미니 진행 바 + 번호 뱃지 + 이름 + 상태.

    Designer는 인자 없는 생성자만 부르므로 번호·이름은 실행 시
    set_step()으로 채운다.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.number = 1
        self.name = ""
        self.state = "pending"    # pending | active | done
        self.percent = 0.0
        self.color = C.BLUE

    def set_step(self, number: int, name: str) -> None:
        self.number, self.name = number, name
        self.update()

    def update_view(self, state: str, percent: float, color: str) -> None:
        self.state, self.percent, self.color = state, percent, color
        self.update()

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)

        done = self.state == "done"
        active = self.state == "active"
        accent = C.GREEN if done else (self.color if active else C.MUTED)
        fill = 100.0 if done else (self.percent if active else 0.0)
        lit = done or active

        # 미니 진행 바
        p.setBrush(QColor(C.L3))
        p.drawRoundedRect(QRectF(0, 0, self.width() - 8, 3), 2, 2)
        if fill > 0:
            p.setBrush(QColor(accent))
            p.drawRoundedRect(QRectF(0, 0, (self.width() - 8) * fill / 100, 3), 2, 2)

        # 번호 뱃지
        badge = QRectF(0, 12, 24, 24)
        p.setBrush(QColor(mix(accent, C.L1, 0.14) if lit else C.L2))
        p.setPen(QPen(QColor(mix(accent, C.L1, 0.32) if lit else C.BORDER), 1))
        p.drawRoundedRect(badge, 6, 6)
        p.setPen(QColor(accent))
        p.setFont(F.mono(9, QFont.Bold))
        p.drawText(badge, Qt.AlignCenter, "✓" if done else str(self.number))

        # 이름
        p.setPen(QColor(accent if lit else C.MUTED))
        p.setFont(F.ui(9, QFont.Bold if active else QFont.Medium))
        p.drawText(QRectF(32, 11, self.width() - 36, 15),
                   Qt.AlignLeft | Qt.AlignVCenter, self.name)

        # 상태
        label = f"{self.percent:.0f}%" if active else ("완료" if done else "대기")
        p.setPen(QColor(C.MUTED))
        p.setFont(F.mono(8))
        p.drawText(QRectF(32, 27, self.width() - 36, 13),
                   Qt.AlignLeft | Qt.AlignVCenter, label)


# ════════════════════════════════════════════════════════════
# 클릭 가능한 카드
# ════════════════════════════════════════════════════════════
class ClickableCard(QFrame):
    """
    QPushButton 안에 레이아웃을 넣으면 자식 라벨이 버튼 경계를 넘어간다.
    그래서 버튼 대신 QFrame을 쓰고 클릭만 직접 처리한다.

    Designer에서는 일반 QFrame처럼 다루면 되고, 안에 라벨을 자유롭게 넣을 수 있다.
    """

    clicked = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._hover = False
        self._base = C.L1
        self._hover_bg = C.L2
        self._border = C.BORDER
        self._hover_border = C.BORDER2
        self.setCursor(Qt.PointingHandCursor)
        self._apply()

    def set_colors(self, base: str, hover_bg: str, border: str, hover_border: str) -> None:
        self._base, self._hover_bg = base, hover_bg
        self._border, self._hover_border = border, hover_border
        self._apply()

    def _apply(self) -> None:
        bg = self._hover_bg if self._hover else self._base
        bd = self._hover_border if self._hover else self._border
        self.setStyleSheet(
            f"ClickableCard {{ background:{bg}; border:1px solid {bd}; border-radius:12px; }}"
            f"QLabel {{ background:transparent; border:none; }}"
        )

    def enterEvent(self, _e):
        self._hover = True
        self._apply()

    def leaveEvent(self, _e):
        self._hover = False
        self._apply()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.rect().contains(event.pos()):
            self.clicked.emit()