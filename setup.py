"""
Setup module
"""

from setuptools import setup

setup(
    name='client_api',
    packages=['client-service', 'service_api'],
    include_package_data=True,
)
