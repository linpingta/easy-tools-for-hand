#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
pipeline.py

"""

import os
import sys
import logging
import argparse
import yaml
import time
from pyutil.program.conf2 import Conf

from sample.sample import Sample, Sample2, Sample3, Sample4
from pattern_eval.pattern_eval import PatternEval


class TaskInfo(object):
    def __init__(self, name, inputs, outputs, conf_filename, status):
        self.name = name
        self.inputs = inputs
        self.outputs = outputs
        self.conf_filename = conf_filename
        self.status = status
        self.depend_num = 0


class Pipeline(object):
    def __init__(self, process_yaml_filename):
        self.process_yaml_filename_ = process_yaml_filename

        self.data_task_dict_ = {}
        self.depend_parent_dict_ = {}
        self.inverse_depend_parent_dict_ = {}
        self.task_info_dict_ = {}

    def _load_yaml(self, logger):
        """
        Load configuration yaml
        :param logger:
        :return:
        """
        return yaml.load(open(self.process_yaml_filename_, 'r'))

    def _build_DAG(self, logger):
        """
        Build task DAG
        :param logger:
        :return:
        """
        yaml_data = self._load_yaml(logger)
        # transfer data
        for task_name, task_info in yaml_data.iteritems():
            unique_task_name = task_info.get("unique_task_name", task_name)
            inputs = task_info.get("inputs", [])
            outputs = task_info.get("outputs", [])
            status = task_info.get("status", 0)
            conf_filename = task_info.get("conf", "")
            self.task_info_dict_[unique_task_name] = TaskInfo(unique_task_name, inputs, outputs, conf_filename, status)

            if not outputs:
                self.data_task_dict_[unique_task_name] = unique_task_name
            else:
                for output in outputs:
                    if output in self.data_task_dict_:  # wrong pattern, two task have same output
                        logger.error("output[%s] duplicate in task[%s]" % (output, unique_task_name))
                        continue
                    self.data_task_dict_[output] = unique_task_name

        # mapping data to name
        for task_name, task_info in self.task_info_dict_.iteritems():
            unique_task_name = task_info.name
            if not task_info.outputs:
                self.inverse_depend_parent_dict_.setdefault(unique_task_name, [])

            if not task_info.inputs:
                self.depend_parent_dict_.setdefault(unique_task_name, [])
            else:
                for input in task_info.inputs:
                    self.depend_parent_dict_.setdefault(unique_task_name, []).append(self.data_task_dict_[input])
                    self.inverse_depend_parent_dict_.setdefault(self.data_task_dict_[input], []).append(unique_task_name)
                    self.task_info_dict_[unique_task_name].depend_num += 1
        logger.debug("depend_partent_dict: %s" % str(self.depend_parent_dict_))
        logger.debug("inverse_depend_partent_dict: %s" % str(self.inverse_depend_parent_dict_))
        return 1

    def _tranfser_to_queue(self, logger):
        """
        简单处理，我们先只支持单线程按顺序处理
        :param logger:
        :return:
        """
        task_queue = []
        already_added_task_len = 0
        while True:
            if already_added_task_len >= len(self.task_info_dict_):
                logger.info("task_len[%s] all task added to queue, break" % already_added_task_len)
                break

            for task_name in sorted(self.depend_parent_dict_, key=lambda k: len(self.depend_parent_dict_[k]),
                                    reverse=True):
                if task_name in task_queue:
                    logger.debug("task_name[%s] already in task_queue" % task_name)
                    continue

                logger.debug("task_name[%s] current depend_num[%s]" % (task_name, self.task_info_dict_[task_name].depend_num))
                if self.task_info_dict_[task_name].depend_num <= 0:
                    task_queue.append(task_name)
                    already_added_task_len += 1
                    logger.debug("task_name[%s] added to task_queue, already_add_task_len[%s]" % (task_name, already_added_task_len))

                    for depend_task_name in self.inverse_depend_parent_dict_[task_name]:
                        self.task_info_dict_[depend_task_name].depend_num -= 1
                        logger.debug("depend_task_name[%s] task_name[%s] depend_num[%s]->[%s]" % (
                        depend_task_name, task_name, self.task_info_dict_[depend_task_name].depend_num+1, self.task_info_dict_[depend_task_name].depend_num))

            time.sleep(1)
        return task_queue

    def _run(self, task_info, logger):
        if task_info.status:
            logger.info("task_name[%s] status[%s] already finish" % (task_info.name, task_info.status))
            return
        logger.info("taks_name[%s] run start" % task_info.name) 
        conf_filename = os.path.join(os.path.dirname(__file__), "conf/%s" % task_info.conf_filename)
        data_path = os.path.join(os.path.dirname(__file__), "data")
        task = globals()[task_info.name](Conf(conf_filename))
        task.run(logger)
        logger.info("taks_name[%s] run finish" % task_info.name) 

    def run(self, logger):
        try:
            if self._build_DAG(logger) < 0:
                logger.error("build DAG fail")
                return

            pipeline_queue = self._tranfser_to_queue(logger)
            for task_name in pipeline_queue:
                if task_name not in self.task_info_dict_:
                    logger.error("task_name[%s] not defined in task_info_dict" % task_name)
                    continue
                task_info = self.task_info_dict_[task_name]
                self._run(task_info, logger)
        except Exception as e:
            logger.exception(e)


def main():
    parser = argparse.ArgumentParser(description="parse argument")
    args = parser.parse_args()

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    Pipeline("pipeline_sample.yaml").run(logger)


if __name__ == '__main__':
    main()
