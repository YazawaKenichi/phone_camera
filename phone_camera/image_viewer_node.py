import cv2
import numpy as np
import rclpy

from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import CompressedImage


class ImageViewer(Node):
    def __init__(self):
        super().__init__('image_viewer')

        self.declare_parameter('topic', '/phone_camera/image/compressed')
        self.declare_parameter('fps', 30.0)

        topic = self.get_parameter('topic').value
        fps = self.get_parameter('fps').value

        self.window_name = topic
        self.latest_msg = None

        # 表示側が遅れても配信側を待たせないよう BEST_EFFORT・最新1枚のみ
        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        self.subscription = self.create_subscription(
            CompressedImage,
            topic,
            self.image_callback,
            qos
        )

        self.get_logger().info(f'viewing: {topic}')

        # デコードと描画はタイマー側で最新フレームだけ行う
        self.timer = self.create_timer(
            1.0 / fps,
            self.timer_callback
        )

    def image_callback(self, msg):
        self.latest_msg = msg

    def timer_callback(self):
        msg = self.latest_msg
        self.latest_msg = None

        if msg is not None:
            frame = cv2.imdecode(
                np.frombuffer(msg.data, dtype=np.uint8),
                cv2.IMREAD_COLOR
            )

            if frame is None:
                self.get_logger().warning('Failed to decode frame')
            else:
                cv2.imshow(self.window_name, frame)

        key = cv2.waitKey(1) & 0xFF
        if key in (ord('q'), 27):
            raise KeyboardInterrupt


def main(args=None):
    rclpy.init(args=args)

    node = ImageViewer()

    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        # Ctrl+C の KeyboardInterrupt が後処理中に遅れて届くことがあるため
        try:
            cv2.destroyAllWindows()
            node.destroy_node()
            rclpy.try_shutdown()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
