#!/usr/bin/env python3
import subprocess

from setuptools import setup
from setuptools.command.build_py import build_py
from setuptools.command.develop import develop
import os
import urllib
import shutil
import sys

try:
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel

    class bdist_wheel(_bdist_wheel):

        def finalize_options(self):
            _bdist_wheel.finalize_options(self)
            # Mark us as not a pure python package
            self.root_is_pure = False

        def get_tag(self):
            python, abi, plat = _bdist_wheel.get_tag(self)
            # We don't link with python ABI, but require python3
            python, abi = 'py3', 'none'
            return python, abi, plat
except ImportError:
    bdist_wheel = None



def compile_ff():
    curr_dir = os.getcwd()
    os.chdir('up_fast_forward/FF-v2.3')    
    print("Building FF (this can take some time)...")
    build = subprocess.run(['make'],
                           stdout = subprocess.PIPE, stderr = subprocess.PIPE,
                           universal_newlines = True)
    print(build.stdout)
    print(build.stderr)
    os.chdir(curr_dir)


class install_ff(build_py):
    """Custom install command."""

    def run(self):
        compile_ff()
        build_py.run(self)


class install_ff_develop(develop):
    """Custom install command."""
    def run(self):
        compile_ff()
        develop.run(self)

long_description = "This package makes the [Fast Forward](https://fai.cs.uni-saarland.de/hoffmann/ff.html) planning system available in the [unified_planning library](https://github.com/aiplan4eu/unified-planning) by the [AIPlan4EU project](https://www.aiplan4eu-project.eu/)."

setup(name='up_fast_forward',
      version='0.0.1',
      description='Unified Planning Integration of the Fast Forward planning system',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='Erez Karpas (wrapper), Joerg Hoffmann (planner)',
      author_email='karpase@technion.ac.il',
      url='https://github.com/aiplan4eu/up-fast-forward/',
      classifiers=['Development Status :: 4 - Beta',
                   'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                   'Programming Language :: Python :: 3',
                   'Topic :: Scientific/Engineering :: Artificial Intelligence'
                   ],
      packages=['up_fast_forward'],
      package_data={
          "": ['fast_forward.py',              
               'FF-v2.3/ff',
                'FF-v2.3/*.c',
                'FF-v2.3/*.h',
                'FF-v2.3/makefile',
                'FF-v2.3/README']
      },
      cmdclass={
          'bdist_wheel': bdist_wheel,
          'build_py': install_ff,
          'develop': install_ff_develop,
      },
      has_ext_modules=lambda: True
      )
