#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
parallel_udpate_data.py

Created on 2018/2/13.
Copyright (c) 2018 Bytedance. All rights reserved.
"""

import os
import sys
import logging
import argparse
import datetime
import time
import ujson as json

from multiprocessing import JoinableQueue, Process

from pyutil.sms.sms_util import send_sms

tgt_check_cmd = "/opt/tiger/yarn_deploy/hadoop/bin/hadoop fs -test -f YOUR_PATH/%s/_SUCCESS"
task_cmd = "python parallel_mock.py --date %s 1>%s.log 2>&1"
old_check_cmd = "/opt/tiger/yarn_deploy/hadoop/bin/hadoop fs -test -f YOUR_PATH/%s"
del_old_cmd = "/opt/tiger/yarn_deploy/hadoop/bin/hadoop fs -rm -r YOUR_PATH/%s"
del_check_year = range(2016, 2019)


def execute_cmd(cmd):
    return os.system(cmd)


def wrapper_result(task_date, status, already_update):
    finished_date_info = {}
    finished_date_info["date"] = task_date
    finished_date_info["status"] = status
    finished_date_info["already_update"] = already_update
    return json.dumps(finished_date_info)


def update_data_each_day(task_queue, result_queue, process_id, logger):
    for task_date in iter(task_queue.get, None):
        try:
            logger.info("process_idx[%s] update task_date[%s]" % (process_id, task_date))
            ret = execute_cmd(tgt_check_cmd % task_date)
            if not ret:  # tgt directory already exists
                result_str = wrapper_result(task_date, "success", 1)
                result_queue.put(result_str)
            else:
                # execute schedule.py
                task_ret = execute_cmd(task_cmd % (task_date, task_date))

                # check hdfs path
                ret = execute_cmd(tgt_check_cmd % task_date)
                if not ret:
                    result_str = wrapper_result(task_date, "success", 0)
                    result_queue.put(result_str)
                else:
                    result_str = wrapper_result(task_date, "fail", 0)
                    result_queue.put(result_str)
        except Exception as e:
            logger.exception("process_idx[%s]: %s" % (process_id, e))
            result_str = wrapper_result(task_date, "success")
            result_queue.put(result_str)
        finally:
            task_queue.task_done()
    task_queue.task_done()


def delete_data(finished_date, delay_num, logger):
    finished_dt = datetime.datetime.strptime(finished_date, '%Y-%m-%d')
    delay_dt = finished_dt + datetime.timedelta(days=delay_num)
    delay_date = delay_dt.strftime("%Y-%m-%d")

    if execute_cmd(old_check_cmd % delay_date):  # already remove
        logger.info("finished_date[%s] delay_date[%s] already removed" % (finished_date, delay_date))
        return 1

    del_cmd = del_old_cmd % delay_date
    del_check_flag = False
    for year in del_check_year: # avoid wrong delete
        if str(year) in del_cmd:
            del_check_flag = True
            break
    if not del_check_flag:
        logger.error("finished_date[%s] delay_date[%s] wrong in del_cmd %s" % (finished_date, delay_date, del_cmd))
        return -1

    logger.info("del_cmd: [%s] " % del_cmd)
    if not execute_cmd(del_cmd):
        logger.info("finished_date[%s] delay_date[%s] remove success" % (finished_date, delay_date))
        return 1
    else:
        logger.info("finished_date[%s] delay_date[%s] remove fail" % (finished_date, delay_date))
        return -1


def notice(date, status, reason, already_finish_flag, logger):
    if already_finish_flag:
        logger.info("notice date[%s] already finish" % date)
        return
    phone_list = ['13621070147']
    for phone in phone_list:
        send_sms("web_alarm", "xFZc5IdRY5JbM", int(phone),
                 "update_pb_job in date[%s] status[%s] with reason[%s], check /ss_ml/ad/train_data/streaming_data_send/ if need" % (
                     date, status, reason))
    logger.info("notice date[%s] notice" % date)


def get_latest_success_delay_date(success_dates, delay_num, logger):
    latest_sucess_dt = datetime.datetime.now()
    for success_date in success_dates:
        success_dt = datetime.datetime.strptime(success_date, '%Y-%m-%d')
        if success_dt < latest_sucess_dt:
            latest_sucess_dt = success_dt
    latest_success_delay_dt = latest_sucess_dt + datetime.timedelta(days=delay_num)
    if latest_sucess_dt == datetime.datetime.now():
        logger.info("get_latest_success_delay_dt, no_change")
        return "-1"
    ret_latest_success_delay_dt = latest_success_delay_dt.strftime("%Y-%m-%d")
    logger.info("get_latest_success_delay_dt[%s]" % ret_latest_success_delay_dt)
    return ret_latest_success_delay_dt


def notice_latest(latest_success_delay_date, already_finish_flag, logger):
    if already_finish_flag:
        logger.info("notice latest_success_delay_date[%s] already finish" % latest_success_delay_date)
        return
    phone_list = ['13621070147']
    for phone in phone_list:
        send_sms("web_alarm", "xFZc5IdRY5JbM", int(phone),
                 "update_pb_job: latest_remove_text_date[%s]" % latest_success_delay_date)
    logger.info("notice latest_success_delay_date[%s] notice" % latest_success_delay_date)


def update_data(args, logger):
    start_date = datetime.datetime.strptime(args.start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(args.end_date, '%Y-%m-%d')
    if start_date > end_date:
        logger.warning("start_date[%s] greater than end_date[%s]" % (args.start_date, args.end_date))
        return True

    task_queue = JoinableQueue()
    result_queue = JoinableQueue()

    finished_date_list = []
    cur_date = end_date
    cnt = 0
    while cur_date >= start_date:
        cur_date_str = cur_date.strftime("%Y-%m-%d")
        task_queue.put(cur_date_str)
        cur_date = cur_date - datetime.timedelta(days=1)
        cnt += 1
    logger.info("run task in [%s] days" % cnt)

    process_list = []
    for i in range(args.parallel):
        process = Process(target=update_data_each_day, args=(task_queue, result_queue, i, logger))
        process_list.append(process)

    for process in process_list:
        process.daemon = True
        process.start()

    logger.info("run task in main process")
    success_dates = []
    failed_dates = []
    while 1:
        if len(finished_date_list) >= cnt:
            logger.info("finish all task with finished_data_list_len[%s], cnt[%s]" % (len(finished_date_list), cnt))
            break

        already_finish_flag = True
        if not result_queue.empty():
            finished_date_info_str = result_queue.get()
            finished_date_info = json.loads(finished_date_info_str)
            finished_date = finished_date_info["date"]
            finished_data_status = finished_date_info["status"]
            logger.info("finished_date[%s] get from result_queue" % finished_date)
            if not int(finished_date_info["already_update"]):
                already_finish_flag = False

            if finished_data_status == "fail":
                logger.warning("finished_date[%s] generate_pb_data failed, already_update_flag[%s]" % (
                    finished_date, already_finish_flag))
                failed_dates.append(finished_date)
                notice(finished_date, 0, "generate_pb_data_failed", already_finish_flag, logger)
            else:
                if finished_date in finished_date_list:
                    logger.error("finished_date[%s] already in finished_date_list, already_update_flag[%s]" % (
                        finished_date, already_finish_flag))
                    failed_dates.append(finished_date)
                    notice(finished_date, 0, "repeated_date_generation", already_finish_flag, logger)
                else:
                    logger.info("finished_date[%s] normal case add to finished_date_list" % finished_date)

                if delete_data(finished_date, args.delay_num, logger) < 0:
                    logger.error("finished_date[%s] delete old_data failed, already_update_flag[%s]" % (
                        finished_date, already_finish_flag))
                    failed_dates.append(finished_date)
                    notice(finished_date, 0, "delete_old_data_failed", already_finish_flag, logger)
                else:
                    logger.info("finished_date[%s] update_success, already_update_flag[%s]" % (
                        finished_date, already_finish_flag))
                    success_dates.append(finished_date)
                    notice(finished_date, 1, "update_pb_success", already_finish_flag, logger)

                latest_success_delay_date = get_latest_success_delay_date(success_dates, args.delay_num, logger)
                if latest_success_delay_date != "-1":
                    notice_latest(latest_success_delay_date, already_finish_flag, logger)
            finished_date_list.append(finished_date)

            with open("success_pb_dates", "w") as fp1:
                json.dump(success_dates, fp1)
            with open("failed_pb_dates", "w") as fp1:
                json.dump(failed_dates, fp1)

        time.sleep(2)

    logger.info("stop subprocess tasks")
    for _ in process_list:
        task_queue.put(None)
    task_queue.join()
    logger.info("run task in main process finish")


def main():
    parser = argparse.ArgumentParser(description="parse argument")
    parser.add_argument('--start_date', type=str, default='2018-02-11')
    parser.add_argument('--end_date', type=str, default='2018-02-12')
    parser.add_argument('--parallel', type=int, default=4)
    parser.add_argument('--retry_max', type=int, default=1)
    parser.add_argument('--delay_num', type=int, default=10)
    args = parser.parse_args()

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    update_data(args, logger)


if __name__ == '__main__':
    main()
