#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
	name='yubikeyedup',
	version='0.1',
	author="Alessio Periloso, scumjr, jaroug",
	author_email="mail@periloso.it",
	license="GPL v3",
	description="Yet Another YubiKey OTP Validation Server",
	long_description=open('README.rst').read(),
	
	packages=find_packages(),
	include_package_data=True,
	classifiers=[
	],
	
	entry_points = {
	    'console_scripts': [
	        'yubikeyedup=src.yubiserve:main',
		'yubikeyedup-dbcreate=tools.dbcreate:main',
		'yubikeyedup-dbconf=tools.dbconf:main',
	    ],
	},
)
