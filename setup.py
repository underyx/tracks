"""Installs tracks"""
from setuptools import setup

setup(
    name='tracks',
    version='0.1.0',
    url='https://github.com/underyx/tracks',
    author='Bence Nagy',
    author_email='bence@underyx.me',
    maintainer='Bence Nagy',
    maintainer_email='bence@underyx.me',
    download_url='https://github.com/underyx/tracks/releases',
    long_description='A library to make AB testing your backend a bit easier.',
    packages=['tracks'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
    ]
)
