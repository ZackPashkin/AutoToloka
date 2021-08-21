import io
import os
import re
from setuptools import setup, find_packages
from pkg_resources import DistributionNotFound, get_distribution


DESCRIPTION = 'Python library for hosting and controlling tasks of the Yandex.Toloka service.'

INSTALL_REQUIRES = ['requests>=2.25.1', 'numpy>=1.20.3', 'Pillow>=8.2.0', 'pandas>=1.2.4', ]

# Reading the contents of the README.md file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as file:
    long_description = file.read()

# Setting up
setup(
    name="autotoloka",
    version='0.0.15',
    author="eftblack",
    author_email="<justlittlemin@gmail.com>",
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
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
    ],
    include_package_data=True
)

