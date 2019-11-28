#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from datetime import datetime

import pymysql
import random
from time import sleep
import logging
from logging import handlers

import coloredlogs


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


class Logger(object):
    level_relations = {
        'debug':logging.DEBUG,
        'info':logging.INFO,
        'warning':logging.WARNING,
        'error':logging.ERROR,
        'crit':logging.CRITICAL
    }

    def __init__(self,filename,level='info',when='D',backCount=100,fmt='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'):
        self.logger = logging.getLogger(filename)
        format_str = logging.Formatter(fmt)
        self.logger.setLevel(self.level_relations.get(level))
        sh = logging.StreamHandler()#往屏幕上输出
        sh.setFormatter(format_str) #设置屏幕上显示的格式
        th = handlers.TimedRotatingFileHandler(filename=filename,when=when,backupCount=backCount,encoding='utf-8')
        th.setFormatter(format_str)#设置文件里写入的格式
        th.setLevel(logging.DEBUG)


        # Initialize coloredlogs.
        coloredlogs.install(level='INFO',fmt="%(asctime)s - %(message)s",
                field_styles=FIELD_STYLES,logger=self.logger)
        #self.logger.addHandler(sh) #把对象加到logger里
        self.logger.addHandler(th)



def insert_ensure(logger, conn, data):
    max_sn = 0
    max_id = 0
    success = False
    while not success:
        try:
            with conn.cursor() as cursor:
                cursor.execute('select max(sn) from record')
                results = cursor.fetchall()
        	for row in results:
        	    max_sn = row[0] or 0
                #print('max_sn',max_sn)
                insert_table_sql = """\
        	    INSERT INTO record(custom,sn)
        	     VALUES('{custom}','{record_sn}')
        	    """
        	cursor.execute(
        	    insert_table_sql.format(custom=data,record_sn=max_sn+1))
        	conn.commit()
                success = True
                #print('%s write %d '%(__file__,max_sn+1))
                logger.debug('%s write %d '%(__file__,max_sn+1))
        except KeyboardInterrupt:
            logger.error('Exit because of Ctrl+C pressed!')
            sys.exit()
        except:
            pass
            #print("write error:", sys.exc_info()[0])

            # print()
        finally:
            pass
            #conn.close()

def main():
    times = 1000
    ip = '127.0.0.1'

    #print(sys.argv)
    argc = len(sys.argv)
    if argc > 1:
        times = int(sys.argv[1])
    if argc > 2:
        ip = sys.argv[2]

    now = datetime.today().strftime('%Y-%m-%d-%H-%M-%S')

    log = Logger('mgr_log_' + now + '.log',level='debug')

    logger = log.logger
    logger.warn('Insert %d records at %s '%(times,ip))

    # 打开数据库连接
    conn = pymysql.connect(host=ip, port=3306, user='root', passwd='Root123*', db='test')
    conn.autocommit(True)

    for i in range(times):
        insert_ensure(logger, conn, __file__ +  ' ' + str(i))
        if i%100 == 0:
            logger.warn('insert %d'%i)
        sleep(random.random()/50)

if __name__ == '__main__':
    main()
