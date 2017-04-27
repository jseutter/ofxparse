
import codecs
import os
import re
import sys

from setuptools import setup, find_packages

# Read the version from __init__ to avoid importing ofxparse while installing.
# This lets the install work when the user does not have BeautifulSoup
# installed.
VERSION = re.search(r"__version__ = '(.*?)'",
                    open("ofxparse/__init__.py").read()).group(1)

REQUIRES = [
    "beautifulsoup4",
    "lxml",
    'six',
]

README = os.path.join(os.path.dirname(__file__), 'README.rst')

with codecs.open(README, encoding='utf8') as f:
    LONG_DESCRIPTION = f.read()

setup_params = dict(
    name='ofxparse',
    version=VERSION,
    description=("Tools for working with the OFX (Open Financial Exchange)"
                 " file format"),
    long_description=LONG_DESCRIPTION,
    # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
    keywords='ofx, Open Financial Exchange, file formats',
    author='Jerry Seutter',
    author_email='jseutter.ofxparse@gmail.com',
    url='http://sites.google.com/site/ofxparse',
    license='MIT License',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=True,
    install_requires=REQUIRES,
    entry_points="""
    """,
    test_suite='tests',
    )

if __name__ == '__main__':
    setup(**setup_params)
