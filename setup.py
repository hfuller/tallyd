#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(name="tallyd",
      version="0.0.1",
      description="tally daemon",
      packages=find_packages(),
      install_requires=["click"],
      entry_points = {
          "console_scripts": [
              "tallyd = tallyd.cli:cli"
          ]
      })
