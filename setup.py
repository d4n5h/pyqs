"""
Setup script for PyQS.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pyqs",
    version="0.1.0",
    author="DanielS",
    author_email="dshlomo4@gmail.com",
    description="A Python port of the Node.js qs library for parsing and stringifying URL query strings",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/d4n5h/pyqs",  # Update with your actual GitHub repository
    project_urls={
        "Bug Tracker": "https://github.com/d4n5h/pyqs/issues",  # Update with your actual GitHub repository
        "Documentation": "https://github.com/d4n5h/pyqs#readme",  # Update with your actual documentation URL
        "Source Code": "https://github.com/d4n5h/pyqs",  # Update with your actual GitHub repository
    },
    packages=find_packages(),
    license="BSD-3-Clause",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    keywords="querystring, url, parse, stringify, qs",
    python_requires=">=3.6",
    install_requires=[],  # Add any dependencies here
    extras_require={}
) 