#!/usr/bin/env python3

import argparse
import sys
import numpy as np
from rclpy.utilities import remove_ros_args
from crazyflie_py import Crazyswarm
from crazyflie_examples.auto_logger import AutoPoseLogger


def parse_args():
    parser = argparse.ArgumentParser(
        description='Muove il drone attraverso uno o piu punti [x y z] passati da terminale.'
    )
    parser.add_argument(
        'coords',
        type=float,
        nargs='+',
        help='Coordinate dei punti: x1 y1 z1 [x2 y2 z2 ...]',
    )
    parser.add_argument(
        '--speed',
        type=float,
        default=0.5,
        help='Velocita media in m/s (default: 0.5)',
    )
    parser.add_argument(
        '--hold',
        type=float,
        default=2.0,
        help='Sosta su ogni punto in secondi (default: 2.0)',
    )
    parser.add_argument(
        '--yaw',
        type=float,
        default=0.0,
        help='Orientamento finale in radianti (default: 0.0)',
    )
    parser.add_argument(
        '--drone',
        type=int,
        default=0,
        help='Indice del drone: 0 = cf_1, 1 = cf_2 (default: 0)',
    )
    parser.add_argument(
        '--relative',
        action='store_true',
        help='Interpreta le coordinate come spostamenti relativi',
    )

    clean_args = remove_ros_args(sys.argv)[1:]
    args = parser.parse_args(clean_args)

    if len(args.coords) % 3 != 0:
        parser.error('Devi inserire 3 numeri (x y z) per ogni punto.')
    if args.speed <= 0:
        parser.error('--speed deve essere maggiore di 0.')

    points = np.array(args.coords, dtype=float).reshape(-1, 3)
    return args, points


def main():
    with AutoPoseLogger('go_to_point'):
        args, points = parse_args()

        swarm = Crazyswarm()
        timeHelper = swarm.timeHelper
        cf = swarm.allcfs.crazyflies[args.drone]

        takeoff_height = 1.0
        cf.takeoff(targetHeight=takeoff_height, duration=2.5)
        timeHelper.sleep(3.5)

        current_pos = np.array(cf.initialPosition, dtype=float)
        current_pos[2] = takeoff_height

        for i, target in enumerate(points, start=1):
            if args.relative:
                distance = np.linalg.norm(target)
                current_pos = current_pos + target
            else:
                distance = np.linalg.norm(target - current_pos)
                current_pos = target

            duration = max(2.0, distance / args.speed)
            print(f'[Punto {i}/{len(points)}] Vado a {target.tolist()} in {duration:.1f} s')

            cf.goTo(
                goal=target,
                yaw=args.yaw,
                duration=duration,
                relative=args.relative,
            )
            timeHelper.sleep(duration + args.hold)

        cf.land(targetHeight=0.04, duration=2.5)
        timeHelper.sleep(3.5)


if __name__ == '__main__':
    main()
