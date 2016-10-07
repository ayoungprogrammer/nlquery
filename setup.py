import pytest
from setuptools import Command, find_packages, setup
import os

class TestCommand(Command):
    description = 'run tests'

    def run(self):
        pytest.main('-x tests')

setup(
    name='nlquery',
    version='0.11',
    packages=find_packages(exclude=["tests", "tests.*", "nlquery-app"]),
    test_suite='tests',
    url='http://github.com/ayoungprogrammer/nlquery',
    cmdclass={
        'testing': TestCommand
    },
    install_requires=[
        'lango',
        'pattern',
        'arrow',
        'grequests',
    ],
)
