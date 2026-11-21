#!/usr/bin/env python3
"""Takeoff-hover-land sicuro per un solo CF con controllo localizzazione UWB."""

from collections import deque
import numpy as np
from geometry_msgs.msg import PoseStamped
from crazyflie_py import Crazyswarm
from crazyflie_examples.auto_logger import AutoPoseLogger

TAKEOFF_DURATION = 2.5
HOVER_DURATION = 5.0
TAKEOFF_DELTA_Z = 1.0


def wait_for_localization(cf, timeHelper, window=15, max_xy=0.10, max_z=0.15, timeout=10.0):
    name = cf.prefix.lstrip('/')
    topic = f'/{name}/pose'

    cf.setParam('kalman.resetEstimation', 1)
    timeHelper.sleep(0.1)
    cf.setParam('kalman.resetEstimation', 0)
    timeHelper.sleep(1.5)

    samples = deque(maxlen=window)

    def on_pose(msg):
        p = msg.pose.position
        samples.append([p.x, p.y, p.z])

    sub = cf.node.create_subscription(PoseStamped, topic, on_pose, 20)

    elapsed = 0.0
    try:
        while elapsed < timeout:
            timeHelper.sleep(0.1)
            elapsed += 0.1
            if len(samples) < window:
                continue
            arr = np.array(samples)
            spread = np.ptp(arr, axis=0)
            if spread[0] < max_xy and spread[1] < max_xy and spread[2] < max_z:
                pos = np.mean(arr, axis=0)
                print(f'[{name}] Localizzato a x={pos[0]:.2f}, y={pos[1]:.2f}, z={pos[2]:.2f} m')
                return pos
    finally:
        cf.node.destroy_subscription(sub)

    raise RuntimeError(f'[{name}] Localizzazione non stabile entro {timeout} s: decollo annullato.')


def main():
    with AutoPoseLogger('safe_hello_world'):
        swarm = Crazyswarm()
        timeHelper = swarm.timeHelper
        cf = swarm.allcfs.crazyflies[0]

        pos0 = wait_for_localization(cf, timeHelper)
        z0 = float(pos0[2])

        cf.takeoff(targetHeight=z0 + TAKEOFF_DELTA_Z, duration=TAKEOFF_DURATION)
        timeHelper.sleep(TAKEOFF_DURATION + HOVER_DURATION)
        cf.land(targetHeight=z0 + 0.04, duration=TAKEOFF_DURATION)
        timeHelper.sleep(TAKEOFF_DURATION + 1.0)


if __name__ == '__main__':
    main()