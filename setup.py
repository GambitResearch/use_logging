from distutils.core import setup

import os
from setuptools import find_packages

DIR = os.path.dirname(__file__)

with open(os.path.join(DIR, "README.md")) as f:
	readme = f.read().splitlines()

setup(
	name='use_logging',
	version='0.0.1',
	packages=find_packages(include='use_logging*'),
	url='https://github.com/GambitResearch/use_logging',
	author='Daniel Royde',
	author_email='danielroyde@gmail.com',
	description=readme[6],
	long_description='\n'.join(readme[3:]).lstrip(),
	keywords=['Python', 'Logging'],
	scripts=['bin/use_logging'],
	license='MIT',
)
