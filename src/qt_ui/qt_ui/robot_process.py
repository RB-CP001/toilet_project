"""Robot Process: runs one toilet_cleaning node as a subprocess.

Every toilet_cleaning entry point follows the same shape - main() sets up
DR_init, imports DSR_ROBOT2 and calls run() - so the full sequence
(cleaning_manager) and each individual step are launched the same way.

Only one robot process may run at a time. Two processes commanding the same
arm would fight over it.
"""

import os
import shutil
import signal
import subprocess
import threading


PACKAGE = "toilet_cleaning"

# Seconds to wait for a graceful SIGINT shutdown before escalating.
SIGINT_GRACE = 5.0
SIGTERM_GRACE = 3.0

# The step nodes log failures and still exit 0, so their stderr is the only
# way to tell a failed run from a successful one.
ERROR_MARKERS = ("Robot Error", "[ERROR]", "Traceback")


# =============================================================
# ROBOT PROCESS
# =============================================================

class RobotProcess:

    def __init__(self, log=None, output=None):

        self.process = None

        # Executable and human-readable label of the current run.
        self.executable = None
        self.label = None

        # Set when the child printed something that looks like a failure.
        self.saw_error = False

        self._log = log
        self._output = output

        self._reader = None

    # =========================================================
    # LOG
    # =========================================================

    def log(self, text):

        if self._log is not None:

            self._log(str(text))

    # =========================================================
    # STATE
    # =========================================================

    def is_running(self):

        if self.process is None:

            return False

        return self.process.poll() is None

    def poll_exit_code(self):
        """Return the exit code once, when the process has just finished."""

        if self.process is None:

            return None

        code = self.process.poll()

        if code is None:

            return None

        self.process = None

        return code

    # =========================================================
    # START
    # =========================================================

    def start(self, executable, label):

        if self.is_running():

            self.log(
                f"{self.label} 실행 중입니다. 먼저 끝나기를 기다리세요."
            )

            return False

        if shutil.which("ros2") is None:

            self.log(
                "'ros2' command not found. "
                "Source the workspace setup.bash before starting the HMI."
            )

            return False

        try:

            self.process = subprocess.Popen(
                [
                    "ros2",
                    "run",
                    PACKAGE,
                    executable,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                # Own process group, so signals reach ros2 run and its child.
                start_new_session=True,
            )

        except OSError as e:

            self.process = None

            self.log(
                f"{label} 실행 실패: "
                f"{type(e).__name__}: {e}"
            )

            return False

        self.executable = executable
        self.label = label
        self.saw_error = False

        # The pipe must be drained on its own thread; a full buffer would
        # block the child mid-motion.
        self._reader = threading.Thread(
            target=self._drain,
            args=(self.process,),
            daemon=True,
        )

        self._reader.start()

        self.log(
            f"{label} 시작 (pid {self.process.pid})"
        )

        return True

    # =========================================================
    # OUTPUT READER
    # =========================================================

    def _drain(self, process):

        try:

            for line in process.stdout:

                line = line.rstrip()

                if not line:
                    continue

                if any(m in line for m in ERROR_MARKERS):

                    self.saw_error = True

                if self._output is not None:

                    self._output(line)

        except (ValueError, OSError):

            # Pipe closed while the process was being torn down.
            pass

    # =========================================================
    # STOP
    # =========================================================

    def stop(self, force=False):
        """Signal the child. Does not block; poll_exit_code() reports the end."""

        if not self.is_running():

            return False

        sig = signal.SIGKILL if force else signal.SIGINT

        self._signal_group(self.process, sig)

        self.log(
            f"{self.label} {'강제 종료' if force else '종료 요청'}"
        )

        return True

    def stop_and_wait(self, force=False):
        """Blocking stop, for application shutdown only."""

        if not self.is_running():

            return False

        process = self.process

        if force:

            self._signal_group(process, signal.SIGKILL)

        else:

            self._signal_group(process, signal.SIGINT)

            if not self._wait(process, SIGINT_GRACE):

                self._signal_group(process, signal.SIGTERM)

                if not self._wait(process, SIGTERM_GRACE):

                    self._signal_group(process, signal.SIGKILL)

        self._wait(process, SIGTERM_GRACE)

        self.process = None

        return True

    # =========================================================
    # SIGNAL HELPERS
    # =========================================================

    def _signal_group(self, process, sig):

        try:

            os.killpg(
                os.getpgid(process.pid),
                sig
            )

        except (ProcessLookupError, PermissionError):

            try:

                process.send_signal(sig)

            except ProcessLookupError:

                pass

    def _wait(self, process, timeout):

        try:

            process.wait(timeout=timeout)

            return True

        except subprocess.TimeoutExpired:

            return False
