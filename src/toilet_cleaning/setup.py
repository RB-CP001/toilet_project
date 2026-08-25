import os 
from glob import glob
from setuptools import find_packages, setup

package_name = 'toilet_cleaning'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('toilet_launch', '*launch.[pxy][yma]*'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='may',
    maintainer_email='maymayko9559@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'cleaning_manager = toilet_cleaning.cleaning_manager:main',
            'detect_lid = toilet_cleaning.detect_lid:main',
            'open_lid = toilet_cleaning.open_lid:main',
            'apply_bleach = toilet_cleaning.apply_bleach:main',
            'brush_clean = toilet_cleaning.brush_clean:main',
            'rinse = toilet_cleaning.rinse:main',
            'finish = toilet_cleaning.finish:main',
        ],
    },
)
