import os
import re
import sys
import platform
import subprocess
import multiprocessing

from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from distutils.version import LooseVersion


class CMakeExtension(Extension):
    def __init__(self, name, sourcedir=''):
        Extension.__init__(self, name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)

class CMakeBuild(build_ext):
    def run(self):
        try:
            out = subprocess.check_output(['cmake', '--version'])
        except OSError:
            raise RuntimeError("CMake must be installed to build the following extensions: " +
                               ", ".join(e.name for e in self.extensions))

        if platform.system() == "Windows":
            raise RuntimeError('Windows is currrently unsupprted due to a lack of interest/funding')

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):

        # this is where setuptools will look for our files to install
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))

        # set some flags for the cmake command line configuring this build
        # specifically we need to put the build where setuptools can find it
        # and also error out when dependencies are not found
        cmake_args = ['-DCMAKE_INSTALL_PREFIX=' + extdir,
                      '-DLIB_PREFIX=.',
                      '-DREQUIRE_PYTHON=TRUE',
                      '-DREQUIRE_MPI=TRUE',
                      '-DREQUIRE_UDUNITS=TRUE',
                      '-DREQUIRE_NETCDF=TRUE',
                      '-DREQUIRE_BOOST=TRUE',]

        # set some command line arguments for cmake
        cfg = 'Debug' if self.debug else 'Release'
        build_args = ['--config', cfg]
        install_args = ['--config', cfg]

        # figure out a reasonable number of cores for the build
        nj = multiprocessing.cpu_count()

        if platform.system() == "Windows":
            raise RuntimeError('Windows is currrently unsupprted due to a lack of interest/funding')
        else:
            cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
            build_args += ['--', '-j20']
            install_args += ['--', '-j%d'%(nj), 'install']

        # make the build directory
        if not os.path.exists(self.build_temp):
            os.makedirs(self.build_temp)

        # builds teca using cmake and installs it where distutils is looking for it
        try:
            subprocess.check_call(['cmake', ext.sourcedir] + cmake_args, cwd=self.build_temp)
            subprocess.check_call(['cmake', '--build', '.'] + build_args, cwd=self.build_temp)
            subprocess.check_call(['cmake', '--build', '.'] + install_args, cwd=self.build_temp)
        except:
            sys.stderr.write('\n')
            sys.stderr.write('================================================================\n')
            sys.stderr.write('  An error ocured building TECA. This is usually a symptom\n')
            sys.stderr.write('  of a missing dependency. The error messages above will indicate\n')
            sys.stderr.write('  which package is missing. Install the development package for\n')
            sys.stderr.write('  the missing dependency using your system\'s package manager\n')
            sys.stderr.write('================================================================\n')
            sys.stderr.write('\n')
            raise

        # generate on the fly the top level python module that can be imported from the
        # setuptools install
        f = open(os.path.join(extdir, 'teca.py'), 'w')
        f.write('import sys, os\n')
        f.write('from teca import *\n')
        f.close()


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='teca',
    version='2.2.0rc1',
    author='Burlen Loring',
    author_email='bloring@lbl.gov',
    description='The Toolkit for Extreme Climate Analysis',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LBL-EESA/TECA",
    classifiers=[
        "Programming Language :: Python",
        "Operating System :: POSIX",
        "Operating System :: MacOS",
        "License :: Other/Proprietary License",
        ],
    ext_modules=[CMakeExtension('teca')],
    cmdclass=dict(build_ext=CMakeBuild),
    zip_safe=False,
    install_requires=[
        "mpi4py",
        "numpy",
        "matplotlib",
        ],
    )

