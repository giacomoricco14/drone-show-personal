#!/usr/bin/env python3

import numpy as np
from crazyflie_py import Crazyswarm
from crazyflie_examples.auto_logger import AutoPoseLogger


def main():
    with AutoPoseLogger('x_shape'):
        # --- Parametri della X ---
        CENTER = np.array([0.0, 0.0])  # Centro della X nel piano XY [cx, cy] (m)
        L = 0.5                        # Semi-ampiezza della X (lato totale = 1.2 m)
        Z1 = 1.0                       # Quota drone 1 (m)
        Z2 = 2.0                       # Quota drone 2 (m) -> 0.7 m di separazione verticale
        # -------------------------

        swarm = Crazyswarm()
        timeHelper = swarm.timeHelper
        cfs = swarm.allcfs.crazyflies

        if len(cfs) != 2:
            raise RuntimeError(
                f'Errore: questo script richiede esattamente 2 droni, trovati {len(cfs)}.'
            )

        cf1, cf2 = cfs[0], cfs[1]
        cx, cy = CENTER

        # 1. Decollo a due altezze diverse
        cf1.takeoff(targetHeight=Z1, duration=2.0)
        cf2.takeoff(targetHeight=Z2, duration=3.0)
        timeHelper.sleep(3.5)


        # 2. Incrocio simultaneo sulle diagonali (disegnano la X vista dall'alto)
        cf1.goTo(np.array([cx + 2*L, cy + 2*L, Z1]), yaw=0.0, duration=8.0)
        cf2.goTo(np.array([cx - 2*L, cy + 2*L, Z2]), yaw=0.0, duration=8.0)
        timeHelper.sleep(6.0)

        # 3. Atterraggio (a fine incrocio distano 1.2 m in orizzontale)
        cf1.land(targetHeight=0.04, duration=2.0)
        cf2.land(targetHeight=0.04, duration=3.0)
        timeHelper.sleep(3.5)


if __name__ == '__main__':
    main()
