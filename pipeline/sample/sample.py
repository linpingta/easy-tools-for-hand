#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sample.py

"""

import os
import sys
import logging
import argparse


class Sample(object):
    def __init__(self, conf):
        self.conf = conf
        print "test sample conf ", self.conf.get("creative_category_path", "")

    def run(self, logger):
        print "run sample ", self.conf


class Sample2(object):
    def __init__(self, conf):
        self.conf = conf

    def run(self, logger):
        print "run sample2 ", self.conf


class Sample3(object):
    def __init__(self, conf):
        self.conf = conf

    def run(self, logger):
        print "run sample3 ", self.conf


class Sample4(object):
    def __init__(self, conf):
        self.conf = conf

    def run(self, logger):
        print "run sample4 ", self.conf


def main():
    parser = argparse.ArgumentParser(description="parse argument")
    args = parser.parse_args()


if __name__ == '__main__':
    main()
