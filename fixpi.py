#!/usr/bin/env python
import sys
import logging

import json
import pexpect
import coloredlogs
from pexpect import pxssh

PI_IP               = '192.168.1.100'
COMMAND_PROMPT      = '[#$] '
FORWARD_IP          = '123.207.155.150'
ROOT_PASSWORD       = 'lc1Clc'
PI_PASSWORD         = 'ucontrol123'
TIMEOUT             = 600

BASE_DIR            = '/interliNQ/ucontrol-client'
CONFIG_FILE         = BASE_DIR + '/config.json'
LOCAL_CONFIG_FILE   = BASE_DIR + '/config.local.json'

TRANSMIT_DIR        = BASE_DIR + '/monitor/transmit'
PENDING_DIR         = BASE_DIR + '/monitor/pending'
TRANSMIT_TAR        = BASE_DIR + '/transmit.tar.gz'
PENDING_TAR         = BASE_DIR + '/pending.tar.gz'

REPLACE_IP_CMD      = 'sudo sed -i "s/54.246.122.56/%s/" %s' % (FORWARD_IP, CONFIG_FILE)
CHECK_IP_CMD        = 'sudo grep "%s" %s' % (FORWARD_IP, CONFIG_FILE)
GZIP_FILE_CMD       = 'sudo tar -jcvf %s %s'
GET_DEVICE_NAME_CMD = 'sudo '



LEVEL_STYLES = {
    'info': {'color': 'green'},
    'critical': {'color': 'red', 'bold': True},
    'error': {'color': 'red'},
    'debug': {},
    'warning': {'color': 'yellow'}}

FIELD_STYLES = {
    'funcName': {'color': 'cyan'},
    'lineno': {'color': 'cyan'},
    'asctime': {'color': 'green'}}

DATE_FORMAT = '%H:%M:%S'
logger = logging.getLogger('fixpi')

# Initialize coloredlogs.
coloredlogs.install(level='DEBUG',fmt="%(asctime)s - %(message)s",field_styles=FIELD_STYLES)
#coloredlogs.install(
#    level='DEBUG',
#    logger=logger,
#    fmt=LOG_FORMAT,
#    datefmt=DATE_FORMAT)
#

def fix1(ip):
    try:
        ssh = pxssh.pxssh()
        username = 'pi'
        password = PI_PASSWORD
        ssh.login (ip, username, password)
        ssh.prompt()             # match the prompt
        print('1')
        ssh.sendline ('su - root')
        ssh.expect(['Password:'])
        ssh.sendline('lc1Clc')
        print('2')
        # ssh.prompt()
        print('3')
        ssh.sendline('cat /interliNQ/ucontrol-client/config.json')
        print(ssh.before)
        ssh.sendline('ls -l')
        ssh.sendline('whoami')
        print('4')
        # ssh.prompt()
        print(ssh.before)
        # ssh.logout()
    except pxssh.ExceptionPxssh as e:
        print("pxssh failed on login.")
        print(str(e))

def ssh_cmd(ip, cmd, expect_str=None):
    ssh = pexpect.spawn('ssh pi@%s' % ip, timeout=TIMEOUT)
    # ssh.logfile = sys.stdout
    try:
        i = ssh.expect(['password:', 'continue connecting (yes/no)?'])
        if i == 0 :
            ssh.sendline(PI_PASSWORD)
        elif i == 1:
            ssh.sendline('yes')
            ssh.expect('password:')
            ssh.sendline(PI_PASSWORD)

        ssh.expect(COMMAND_PROMPT)
        ssh.sendline(cmd)
        if not expect_str:
            ssh.expect (COMMAND_PROMPT)
            return True
        else:
            i = ssh.expect(expect_str)
            #print(ssh.before)
            if i == 0:
                return True
            else:
                return False

        #ssh.sendline ('uname -a')
        #ssh.expect (COMMAND_PROMPT)
        #print(ssh.before)
        #ssh.expect(pexpect.EOF)

        #ssh.expect(COMMAND_PROMPT)

        #print(ssh.before)
        #ssh.sendline('ls')
        #ssh.sendline('su')
        #ssh.expect('.assword:')
        #ssh.sendline(ROOT_PASSWORD)
        #ssh.expect('root*')
        #ssh.sendline(REPLACE_IP_CMD)
        #r = ssh.read()
        #print(r)
    except pexpect.TIMEOUT:
        print("TIMEOUT")
        ssh.close()

def scp_cmd(ip, remote_dir, local_dir='./'):
    ssh = pexpect.spawn('scp -r pi@%s:%s %s' % (ip, remote_dir, local_dir), timeout=TIMEOUT)
    ssh.logfile = sys.stdout
    try:
        i = ssh.expect(['password:', 'continue connecting (yes/no)?'])
        if i == 0 :
            ssh.sendline(PI_PASSWORD)
        elif i == 1:
            ssh.sendline('yes')
            ssh.expect('password:')
            ssh.sendline(PI_PASSWORD)
        #ssh.expect(COMMAND_PROMPT)
        ssh.expect(pexpect.EOF)
    except pexpect.TIMEOUT:
        print("TIMEOUT")
        ssh.close()


if __name__ == '__main__':
    #data = json.load(open('config.local.json'))
    #device_name = data['name'].replace(' ','')
    #print(device_name)
    #sys.exit(1)
    if len(sys.argv) == 2:
        pi_ip = sys.argv[1]
    else:
        print('Assume YOUR_RASBERRYPI_IP is %s' % PI_IP)
        pi_ip = PI_IP

    ssh_cmd(pi_ip, REPLACE_IP_CMD)
    # sys.exit(1)
    if ssh_cmd(pi_ip, CHECK_IP_CMD, '"server"'):
        logger.warn('Modify Success!!')
    else:
        logger.error('Modify Failed!!')

    scp_cmd(pi_ip, LOCAL_CONFIG_FILE)
    data = json.load(open('config.local.json'))
    device_name = data['name'].replace(' ','')
    pexpect.run('mkdir %s' % device_name)

    ssh_cmd(pi_ip, GZIP_FILE_CMD % (TRANSMIT_TAR,TRANSMIT_DIR))
    scp_cmd(pi_ip, TRANSMIT_TAR, './%s/'%device_name)

    ssh_cmd(pi_ip, GZIP_FILE_CMD % (PENDING_TAR,PENDING_DIR))
    scp_cmd(pi_ip, PENDING_TAR, './%s/'%device_name)
