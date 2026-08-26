"""Manager Process: runs the toilet_cleaning cleaning_manager node as a subprocess.

The cleaning_manager has no start trigger of its own; its main() starts the
cleaning sequence as soon as the process comes up, and DSR_ROBOT2 spins the
manager node internally. Running it in a separate process is therefore the only
way to drive it from the HMI without touching the toilet_cleaning package.
"""

import os
import shutil
import signal
import subprocess


PACKAGE = "toilet_cleaning"
EXECUTABLE = "cleaning_manager"

# Seconds to wait for a graceful SIGINT shutdown before escalating.
SIGINT_GRACE = 5.0
SIGTERM_GRACE = 3.0


# =============================================================
# MANAGER PROCESS
# =============================================================

class ManagerProcess:

    def __init__(self, log=None):

        self.process = None

        self._log = log

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

    def start(self):

        if self.is_running():

            self.log(
                "cleaning_manager is already running"
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
                    EXECUTABLE,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                # Own process group, so signals reach ros2 run and its child.
                start_new_session=True,
            )

        except OSError as e:

            self.process = None

            self.log(
                f"Failed to start cleaning_manager: "
                f"{type(e).__name__}: {e}"
            )

            return False

        self.log(
            f"cleaning_manager started (pid {self.process.pid})"
        )

        return True

    # =========================================================
    # STOP
    # =========================================================

    def stop(self, force=False):

        if not self.is_running():

            self.log(
                "cleaning_manager is not running"
            )

            return False

        process = self.process

        if force:

            self._signal_group(process, signal.SIGKILL)

            self.log(
                "cleaning_manager killed"
            )

        else:

            self._signal_group(process, signal.SIGINT)

            if not self._wait(process, SIGINT_GRACE):

                self._signal_group(process, signal.SIGTERM)

                if not self._wait(process, SIGTERM_GRACE):

                    self._signal_group(process, signal.SIGKILL)

            self.log(
                "cleaning_manager stopped"
            )

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
