#!/bin/bash

cur_dir=`pwd`

# substitue base_checker to real checker
cd $cur_dir/bin &&  celery -A scheduler worker --loglevel=INFO --beat
