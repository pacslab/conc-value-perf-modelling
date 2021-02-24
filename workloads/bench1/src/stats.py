
#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import print_function
import json
import time
import os
import socket
import sys
import uuid
import subprocess

try:
    import urllib2
    from urllib2 import urlopen
except BaseException:
    from urllib.request import urlopen

import decimal


# Set it to your own servers
INST_PRIV_IP_DST = "8.8.8.8"
VM_PUB_ID_DST = "https://api.ipify.org/"


def fstr(f):
    """
    Convert a float number to string
    """
    ctx = decimal.Context()
    ctx.prec = 20
    d1 = ctx.create_decimal(repr(f))
    return format(d1, 'f')


def get_meminfo():
    """
    Get and format the content of /proc/meminfo
    """
    buf = open('/proc/meminfo').read()
    buf = ','.join([v.replace(' ', '') for v in
                    buf.split('\n') if v])

    return buf


def get_vmstat():
    """
    Get and format the content of /proc/vmstat
    """
    buf = open("/proc/vmstat").read()
    buf = [v.replace(' ', ":") for v in buf.split("\n")]
    buf = ";".join(buf)
    return buf


def get_diskstat():
    """
    Get and format the content of /proc/diskstats
    """
    buf = open("/proc/diskstats").read()
    buf = [v for v in buf.split("\n") if v]
    buf = [
        v.replace(
            " ",
            ",").replace(
            ",,,,,,,",
            ",").replace(
                ",,,",
            "").lstrip(",") for v in buf]
    buf = ";".join(buf)
    return buf


def get_cpuinfo():
    """
    Get and format the content of /proc/cpuinfo
    """
    buf = "".join(open("/proc/cpuinfo").readlines())
    cpuinfo = buf.replace("\n", ";").replace("\t", "")
    return cpuinfo


def get_cpuinfo_short():
    """ Get CPU version information """
    buf = "".join(open("/proc/cpuinfo").readlines())
    cpuinfo = buf.replace("\n", ";").replace("\t", "")
    a1 = cpuinfo.count("processor")
    a2 = cpuinfo.split(";")[4].split(":")[1].strip()
    return "%s,%s" % (a1, a2)
    # return [a1, a2.split(' @ ')[0], a2.split(' @ ')[1]]


def get_inst_id():
    """ Get the inst ID """
    log_file = '/tmp/inst_id.txt'
    new_id = str(uuid.uuid4())
    try:
        exist_id = open(log_file).read().strip('\n')
    except BaseException:
        open(log_file, 'w').write(new_id)
        exist_id = new_id
    return exist_id, new_id


def get_inst_priv_ip():
    """ Get inst private IP """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((INST_PRIV_IP_DST, 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


def get_vm_priv_ip():
    """ Get VM private IP """
    ip = socket.gethostbyname(socket.getfqdn())
    return ip


def get_vm_pub_ip():
    """ Get VM public IP by querying external server """
    ip = "None"
    try:
        ip = str(urlopen(VM_PUB_ID_DST).read().decode())
    except BaseException:
        pass
    return ip


def get_vm_id():
    """ Get VM ID from /proc/self/cgroup """
    buf = open('/proc/self/cgroup').read().split('\n')[-3].split('/')
    vm_id, inst_id = buf[1], buf[2]
    return vm_id, inst_id


def get_uptime():
    """ Get VM uptime """
    uptime = ','.join(open('/proc/uptime').read().strip('\n').split(' '))
    return uptime


def stat_other():
    hostname = os.popen('uname -n').read().strip('\n')
    kernel_ver = os.popen('uname -r').read().strip('\n')
    return [hostname, kernel_ver]


def stat_basic(argv=1):

    exist_id, new_id = get_inst_id()
    vm_id, inst_id = get_vm_id()
    uptime = get_uptime()
    vm_priv_ip = get_vm_priv_ip()
    # This causes some slow-downs!
    # vm_pub_ip = get_vm_pub_ip()
    vm_pub_ip = vm_priv_ip
    inst_priv_ip = get_inst_priv_ip()
    cpu_info = get_cpuinfo_short()

    res = {
        'exist_id': exist_id,
        'new_id': new_id,
        'vm_id': vm_id,
        'inst_id': inst_id,
        'vm_priv_ip': vm_priv_ip,
        'vm_pub_ip': vm_pub_ip,
        'inst_priv_ip': inst_priv_ip,
        'uptime': uptime,
        'cpu_info': cpu_info
    }

    # TEST
    # Simulate long cold start
    # if exist_id == new_id: # if cold start
    #     start_time = time.time()
    #     while time.time() - start_time < 20:
    #         continue

    return res


if __name__ == '__main__':
    func_name = sys.argv[1]
    res = eval(func_name)()
    print(res)
