import sys, os, subprocess

hadoop_bin_path ="bin/hadoop"

def run_cmd_silent(cmd, func=None):
    print "-" * 80
    print cmd
    res = []
    process = subprocess.Popen(cmd,
                       shell=True,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT)
    for t, line in enumerate(iter(process.stdout.readline,'')):
        if func:
            func(line)
        if line.strip():
            res.append(line.strip())
        if t % 5 == 0:
            sys.stdout.flush()
    process.communicate()
    sys.stdout.flush()
    return process.returncode, res

def delete_hadoop(output_path):
    if not output_path:
        return False
    if rm_hdfs_file(output_path):
        if os.system("%s fs -rm -r %s" % (hadoop_bin_path, output_path)) != 0:
            return False
        return True

def get_file_from_hdfs(hdfs_path, local_path):
    if os.system("%s fs -text %s/* > %s" % (hadoop_bin_path, hdfs_path.strip(), local_path.strip())) != 0:
        return False
    return True

def rm_hdfs_file(path):
    cmd = "%s fs -test -e %s" % (hadoop_bin_path, path)
    ret, _ = run_cmd_silent(cmd)

