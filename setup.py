#!/usr/bin/env python3
"""Setup script for SQLiteExplorer."""

from setuptools import setup, find_packages
from pathlib import Path

long_description = Path("README.md").read_text(encoding="utf-8")

setup(
    name="sqliteexplorer",
    version="1.0.0",
    description="Smart SQLite Database Explorer & Management Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="ATLAS (Team Brain)",
    author_email="logan@metaphy.com",
    url="https://github.com/DonkRonk17/SQLiteExplorer",
    py_modules=["sqliteexplorer"],
    python_requires=">=3.7",
    install_requires=[],  # Zero dependencies
    entry_points={
        "console_scripts": [
            "sqliteexplorer=sqliteexplorer:main",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    keywords="sqlite database explorer cli tool query export",
    license="MIT",
)
