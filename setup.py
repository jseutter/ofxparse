import re
import sys

from setuptools import setup, find_packages

# Read the version from __init__ to avoid importing ofxparse while installing.
# This lets the install work when the user does not have BeautifulSoup
# installed.
VERSION = re.search(r"__version__ = '(.*?)'",
                    open("ofxparse/__init__.py").read()).group(1)

# Use BeautifulSoup 3 on Python 2.5 and earlier and BeautifulSoup 4 otherwise
if sys.version_info < (2, 6):
    REQUIRES = [
        "beautifulSoup>=3.0",
    ]
else:
    REQUIRES = [
        "beautifulsoup4"
    ]

if sys.version_info < (2, 7):
    REQUIRES.extend([
        "ordereddict>=1.1",
    ])

REQUIRES.extend([
    'six',
    'lxml'
])

setup_params = dict(
    name='ofxparse',
    version=VERSION,
    description=("Tools for working with the OFX (Open Financial Exchange)"
                 " file format"),
    long_description=open("./README", "r").read(),
    # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
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
