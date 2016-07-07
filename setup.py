import os
import time
import shutil
import random
import subprocess
from distutils.errors import LibError
from setuptools import setup
from distutils.command.build import build as _build
from setuptools.command.develop import develop as _develop


class build(_build):
    def run(self):
            self.execute(_build_qemus, (), msg="Building Tracer QEMU")
            _build.run(self)

class develop(_develop):
    def run(self):
            self.execute(_build_qemus, (), msg="Building Tracer QEMU")
            _develop.run(self)

cmdclass = {'build': build, 'develop': develop}

setup(
    name='tracer', version='0.1', description="Symbolically trace concrete inputs.",
    packages=['tracer'],
    data_files=[ ],
    cmdclass=cmdclass,
    install_requires=[ 'shellphish-qemu' ],
)
