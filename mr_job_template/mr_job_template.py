#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
mr_job_template.py
"""

import os
import sys
import logging
import argparse
from utils import delete_hadoop


class CommonMR(object):
    def __init__(self):
        self.param_dict_ = {
            "mapred.job.map.memory.mb": 2000,
            "mapred.child.java.opts": "-Xmx3000m",
            "mapred.job.name": "default_mr_chutong",
            "mapred.reduce.slowstart.completed.maps": 0.90,
            "mapred.min.split.size": 1000000000,
            "mapred.reduce.tasks": 200,
            "mapreduce.input.combinefileformat.tasks": 1000,
            "mapred.job.reduce.memory.mb": 20000,
            "mapred.output.compress": True,
            "stream.map.input.ignoreKey": True,
        }

    def update_param_dict(self, new_dict):
        self.param_dict_.update(new_dict)

    @property
    def mapper(self):
        return self.mapper_

    @mapper.setter
    def mapper(self, value):
        self.mapper_ = value

    @property
    def reducer(self):
        return self.reducer_

    @reducer.setter
    def reducer(self, value):
        self.reducer_ = value

    @property
    def input(self):
        return self.input_

    @input.setter
    def input(self, value):
        self.input_ = value

    @property
    def output(self):
        return self.output_

    @output.setter
    def output(self, value):
        self.output_ = value

    @property
    def file(self):
        return self.file_

    @file.setter
    def file(self, value):
        if isinstance(value, str):
            self.file_ = value
        else:
            self.file_ = ' '.join(value)

    def _generate_cmd(self):
        cmd = "mr" \
              " -libjars hadoop-2.6.0-cdh5.4.4/bytedance-data-1.0.1.jar "
        for param_key, param_value in self.param_dict_.iteritems():
            t_param_value = param_value
            if param_value == True:
                t_param_value = "true"
            elif param_value == False:
                t_param_value = "false"
            line = " -D" + str(param_key) + "=" + str(t_param_value)
            cmd += line
        cmd += " -inputformat com.bytedance.data.CustomCombineFileInputFormat"
        cmd += " -mapper '%s'" % self.mapper_
        cmd += " -reducer '%s'" % self.reducer_
        cmd += " -input %s" % self.input_
        cmd += " -output %s" % self.output_
        cmd += " -file %s" % self.file_
        return cmd

    def print_cmd(self):
        print self._generate_cmd()
        return 1

    def run(self, logger, delete_output=0):
        cmd = self._generate_cmd()
        logger.info("task_cmd: [%s]" % cmd)
        if delete_output and self.output_:
            delete_hadoop(self.output_, delete_output)
        if os.system(cmd) != 0:
            return False
        return True


def main():
    parser = argparse.ArgumentParser(description="parse argument")
    args = parser.parse_args()


if __name__ == '__main__':
    main()
