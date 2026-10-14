import os

from glob import glob
from setuptools import setup

package_name = 'phone_camera'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name]
        ),
        (
            'share/' + package_name,
            ['package.xml']
        ),
        (
            os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')
        ),
        (
            os.path.join('share', package_name, 'config'),
            glob('config/*.yaml')
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='yazawa',
    maintainer_email='todo@todo.todo',
    description='Publish smartphone camera stream as ROS 2 CompressedImage',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'phone_camera_node = phone_camera.phone_camera_node:main',
            'image_viewer_node = phone_camera.image_viewer_node:main',
        ],
    },
)

