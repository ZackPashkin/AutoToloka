import io
import os
import re
from setuptools import setup, find_packages
from pkg_resources import DistributionNotFound, get_distribution


DESCRIPTION = 'library for hosting and controlling tasks for Y.Toloka'

INSTALL_REQUIRES = ['requests>=2.25.1', 'numpy>=1.20.3', 'Pillow>=8.2.0', 'pandas>=1.2.4', ]


# Setting up
setup(
    name="autotoloka",
    version='0.0.1',
    author="eftblack",
    author_email="<justlittlemin@gmail.com>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires= ['requests>=2.25.1', 'numpy>=1.20.3', 'Pillow>=8.2.0', 'pandas>=1.2.4','yadisk>=1.2.14' ],
    keywords=['python'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ]
)

