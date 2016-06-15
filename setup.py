"""Installs tracks"""
import io
from setuptools import setup

with io.open('README.rst', encoding='utf-8') as f:
    README = f.read()

setup(
    name='tracks',
    version='0.1.0',
    url='https://github.com/underyx/tracks',
    author='Bence Nagy',
    author_email='bence@underyx.me',
    maintainer='Bence Nagy',
    maintainer_email='bence@underyx.me',
    download_url='https://github.com/underyx/tracks/releases',
    description='Simple A/B testing for your backend',
    long_description=README,
    packages=['tracks'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
    ]
)
