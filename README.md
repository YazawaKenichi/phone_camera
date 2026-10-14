# phone_camera

スマートフォンのカメラ映像（IP Webcam 等でストリーミングされた MJPEG/HTTP 映像）を購読し、ROS 2 の `sensor_msgs/CompressedImage` トピックとして配信する ROS 2 パッケージです。

## 概要

- `camera_url` で指定した URL に OpenCV (`cv2.VideoCapture`) で接続し、映像フレームを取得します。
- 取得したフレームを JPEG エンコードし、`/phone_camera/image/compressed` トピックに 30Hz で配信します。

## 依存関係

- ROS 2 (rclpy)
- sensor_msgs
- OpenCV (`python3-opencv` など、`cv2` が import できる環境)

## パラメータ

| パラメータ名 | 型 | デフォルト値 | 説明 |
| --- | --- | --- | --- |
| `camera_url` | string | `http://192.168.0.123:8080/video` | スマートフォンのカメラ映像配信 URL（例: IP Webcam アプリの映像 URL） |

`config/phone_camera.yaml` で `camera_url` を設定できます。

```yaml
phone_camera:
  ros__parameters:
    camera_url: "http://192.168.3.45:8080/video"
```

## トピック

| トピック名 | 型 | 説明 |
| --- | --- | --- |
| `/phone_camera/image/compressed` | `sensor_msgs/msg/CompressedImage` | JPEG エンコードされたカメラ映像 |

## ビルド

```bash
colcon build --packages-select phone_camera
source install/setup.bash
```

## 実行方法

### launch ファイルを使う場合

```bash
ros2 launch phone_camera phone_camera.launch.py
```

`config/phone_camera.yaml` のパラメータが読み込まれます。

### USB ウェブカメラを使う場合

`camera_url` に `/dev/video*` や `/dev/v4l/by-id/...` のデバイスパスを指定すると、V4L2 (MJPG) で USB カメラから取得します。`width` / `height` / `fps` / `frame_id` パラメータも指定できます。

```bash
ros2 launch phone_camera phone_camera.launch.py \
  params_file:=$(ros2 pkg prefix phone_camera)/share/phone_camera/config/usb_camera.yaml
```

### 配信中の映像を表示する

`view:=true` を付けると、配信中のトピックをウィンドウに表示する `image_viewer_node` も起動します（`q` / `Esc` で閉じます）。
表示ノードは配信ノードとは別プロセスで、BEST_EFFORT・キュー長 1 で購読するため、表示が遅れても配信側には影響しません。

```bash
ros2 launch phone_camera phone_camera.launch.py view:=true
```

すでに配信中のノードに対して、表示だけを後から起動することもできます。

```bash
ros2 run phone_camera image_viewer_node --ros-args -p topic:=/phone_camera/image/compressed
```

### ノードを直接実行する場合

```bash
ros2 run phone_camera phone_camera_node --ros-args -p camera_url:=http://192.168.3.45:8080/video
```

## ライセンス

MIT
