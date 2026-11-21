#!/usr/bin/env python3

import argparse
import csv
import math
import os
import re
import signal
import sys
from datetime import datetime

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.utilities import remove_ros_args
from geometry_msgs.msg import PoseStamped


DEFAULT_LOG_DIR = '/home/user/ros2_ws/src/flight_logs'
POSE_TOPIC_RE = re.compile(r'^/(cf[^/]*)/pose$')


def quat_to_euler(qx, qy, qz, qw):
    sinr_cosp = 2.0 * (qw * qx + qy * qz)
    cosr_cosp = 1.0 - 2.0 * (qx * qx + qy * qy)
    roll = math.atan2(sinr_cosp, cosr_cosp)

    sinp = max(-1.0, min(1.0, 2.0 * (qw * qy - qz * qx)))
    pitch = math.asin(sinp)

    siny_cosp = 2.0 * (qw * qz + qx * qy)
    cosy_cosp = 1.0 - 2.0 * (qy * qy + qz * qz)
    yaw = math.atan2(siny_cosp, cosy_cosp)
    return roll, pitch, yaw


class AutoPoseCsvLogger(Node):
    def __init__(self, output_path):
        super().__init__('pose_csv_logger')
        self.t0 = None
        self.count = 0
        self.output_path = output_path
        self.subscribed_drones = set()
        self.subs = []

        self.file = open(output_path, 'w', newline='')
        self.writer = csv.writer(self.file)
        self.writer.writerow(['t', 'drone', 'x', 'y', 'z', 'roll', 'pitch', 'yaw'])

        self.create_timer(0.25, self.discover_drones)
        self.discover_drones()
        self.get_logger().info(f'Auto-logging attivo -> {output_path}')

    def discover_drones(self):
        for topic_name, topic_types in self.get_topic_names_and_types():
            if 'geometry_msgs/msg/PoseStamped' not in topic_types:
                continue
            match = POSE_TOPIC_RE.match(topic_name)
            if not match:
                continue
            # Si iscrive SOLO se esiste almeno un publisher reale (evita topic fantasma)
            if self.count_publishers(topic_name) == 0:
                continue

            drone_name = match.group(1)
            if drone_name in self.subscribed_drones:
                continue

            sub = self.create_subscription(
                PoseStamped,
                topic_name,
                lambda msg, d=drone_name: self.callback(msg, d),
                50,
            )
            self.subs.append(sub)
            self.subscribed_drones.add(drone_name)
            self.get_logger().info(f'Aggiunto al CSV: {topic_name}')

    def callback(self, msg, drone_name):
        t_abs = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        if t_abs == 0.0:
            t_abs = self.get_clock().now().nanoseconds * 1e-9

        if self.t0 is None:
            self.t0 = t_abs
        t = t_abs - self.t0

        p = msg.pose.position
        q = msg.pose.orientation
        roll, pitch, yaw = quat_to_euler(q.x, q.y, q.z, q.w)

        self.writer.writerow([
            f'{t:.4f}',
            drone_name,
            f'{p.x:.6f}',
            f'{p.y:.6f}',
            f'{p.z:.6f}',
            f'{roll:.6f}',
            f'{pitch:.6f}',
            f'{yaw:.6f}',
        ])
        self.count += 1
        if self.count % 20 == 0:
            self.file.flush()

    def close(self):
        if not self.file.closed:
            self.file.flush()
            self.file.close()
            self.get_logger().info(f'Salvati {self.count} campioni in {self.output_path}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', type=str, default='flight')
    parser.add_argument('--dir', type=str, default=DEFAULT_LOG_DIR)
    args = parser.parse_args(remove_ros_args(sys.argv)[1:])

    os.makedirs(args.dir, exist_ok=True)
    colcon_ignore = os.path.join(args.dir, 'COLCON_IGNORE')
    if not os.path.exists(colcon_ignore):
        open(colcon_ignore, 'a').close()

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = os.path.join(args.dir, f'{args.name}_{timestamp}.csv')

    rclpy.init()
    node = AutoPoseCsvLogger(output_path)

    def handle_sigterm(signum, frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, handle_sigterm)

    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.close()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()