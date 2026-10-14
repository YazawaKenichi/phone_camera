import cv2
import rclpy

from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage


class PhoneCamera(Node):
    def __init__(self):
        super().__init__('phone_camera')

        self.declare_parameter(
            'camera_url',
            'http://192.168.0.123:8080/video'
        )

        camera_url = self.get_parameter(
            'camera_url'
        ).get_parameter_value().string_value

        self.declare_parameter('width', 0)
        self.declare_parameter('height', 0)
        self.declare_parameter('fps', 30.0)
        self.declare_parameter('frame_id', 'phone_camera')

        width = self.get_parameter('width').value
        height = self.get_parameter('height').value
        fps = self.get_parameter('fps').value
        self.frame_id = self.get_parameter('frame_id').value

        self.get_logger().info(f'camera_url: {camera_url}')

        self.publisher = self.create_publisher(
            CompressedImage,
            '/phone_camera/image/compressed',
            10
        )

        if camera_url.startswith('/dev/') or camera_url.isdigit():
            # USB カメラ (V4L2 デバイス)
            device = int(camera_url) if camera_url.isdigit() else camera_url
            self.cap = cv2.VideoCapture(device, cv2.CAP_V4L2)
            self.cap.set(
                cv2.CAP_PROP_FOURCC,
                cv2.VideoWriter_fourcc(*'MJPG')
            )
            if width > 0 and height > 0:
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.cap.set(cv2.CAP_PROP_FPS, fps)
        else:
            self.cap = cv2.VideoCapture(camera_url)

        if not self.cap.isOpened():
            raise RuntimeError(
                f'Failed to open camera stream: {camera_url}'
            )

        self.timer = self.create_timer(
            1.0 / fps,
            self.timer_callback
        )

    def timer_callback(self):
        ret, frame = self.cap.read()

        if not ret:
            self.get_logger().warning('Failed to read frame')
            return

        ret, encoded = cv2.imencode(
            '.jpg',
            frame,
            [cv2.IMWRITE_JPEG_QUALITY, 90]
        )

        if not ret:
            self.get_logger().warning('Failed to encode frame')
            return

        msg = CompressedImage()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self.frame_id
        msg.format = 'jpeg'
        msg.data = encoded.tobytes()

        self.publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)

    node = PhoneCamera()

    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        # Ctrl+C の KeyboardInterrupt が後処理中に遅れて届くことがあるため
        try:
            node.cap.release()
            node.destroy_node()
            rclpy.try_shutdown()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
