#!/bin/bash

cur_dir=`pwd`

# substitue base_checker to real checker
cd $cur_dir && python bin/base_checker.py
