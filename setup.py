from glob import glob
from setuptools import setup
p = 'mpd_bringup'
setup(
    name=p, version='0.1.0', packages=[p],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + p]),
        ('share/' + p, ['package.xml']),
        ('share/' + p + '/launch', glob('launch/*.launch.py')),
        ('share/' + p + '/config', glob('config/*.yaml')),
        ('share/' + p + '/rviz', glob('rviz/*.rviz')),
    ],
    install_requires=['setuptools'], zip_safe=True,
    maintainer='Achraf Aroua', maintainer_email='arouaachref8@gmail.com',
    description='Exploration bringup', license='MIT',
)
