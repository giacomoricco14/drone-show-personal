import os
import signal
import subprocess
import time


class AutoPoseLogger:
    def __init__(self, name='flight'):
        self.name = name
        self.proc = None

    def __enter__(self):
        self.proc = subprocess.Popen(
            ['ros2', 'run', 'crazyflie_examples', 'pose_logger', '--name', self.name],
            start_new_session=True,
        )
        time.sleep(0.8)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.proc and self.proc.poll() is None:
            try:
                os.killpg(self.proc.pid, signal.SIGINT)
                self.proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                os.killpg(self.proc.pid, signal.SIGTERM)
                self.proc.wait(timeout=2)
            except ProcessLookupError:
                pass