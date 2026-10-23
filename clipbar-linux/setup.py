#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="clipbar",
    version="1.0.0",
    description="Clipboard manager for Linux that never loses what you type",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Sajjad Mohabati",
    url="https://github.com/SajjadMohabati/clipbar-mac",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "PyQt6>=6.4.0",
        "cryptography>=3.4",
    ],
    extras_require={
        "pyside": ["PySide6>=6.4.0"],
        "ocr": ["pytesseract>=0.3.10", "Pillow>=9.0.0"],
        "drafts": ["PyGObject>=3.42"],
        "hotkey": ["pynput>=1.7.6"],
    },
    entry_points={
        "console_scripts": [
            "clipbar=clipbar.main:main",
        ],
    },
    classifiers=[
        "Environment :: X11 Applications :: Qt",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Topic :: Desktop Environment",
        "Topic :: Utilities",
    ],
)
