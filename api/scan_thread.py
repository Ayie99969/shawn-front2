# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.dirname(sys.path[0]))
import datetime
import os, time
import threading

import paramiko

from api.scan import ScanApi
from api.ssh import SSHConnect
from common.config import ConfigIni
from common.utils import get_root_path, save_export_to_txt

rlock = threading.RLock()

curPosition = 0  # 初始化位置为文件其实位置
result = 0


class Reader(threading.Thread):
    def __init__(self, res, host, username, port, password, key, report_file):
        self.res = res
        self.host = host
        self.username = username
        self.port = port
        self.password = password
        self.key = key
        self.report_file = report_file
        self.scan_ssh = SSHConnect(self.host, self.username, self.port, self.password, self.key)
        self.scan_ssh.connect()
        super(Reader, self).__init__()  # 调用子类构造函数获得文件大小

    def run(self):  # 线程函数
        global curPosition
        global result
        fstream = open(self.res.fileName, 'r')  # 打开文件
        while True:
            rlock.acquire()
            startPosition = curPosition  # 每次更新起始位置
            if (startPosition + self.res.fileSize / threadNum) < self.res.fileSize:  # 这里，例如开了10个线程，就将文件分为10块，每个线程负责一块
                curPosition = endPosition = (startPosition + self.res.fileSize / threadNum)
            else:
                curPosition = endPosition = self.res.fileSize
            rlock.release()

            if startPosition == self.res.fileSize:
                break
            elif startPosition != 0:  # 这种情况适用于除了第一个文件块之后的文件块，因为分割后，第一块以后的文件块的起始位置肯定比0大
                fstream.seek(startPosition)  # 找到那个位置
                fstream.readline()  # 由于这一行在上一个循环中已经读取了，所以先读一行，把这行跳过
            pos = fstream.tell()  # 获取当前的位置
            while pos <= endPosition:
                print('当前位置：'+str(pos))
                line = fstream.readline()
                print('真正更新文件的节点:'+line.strip('\n'))
                '''
                    对每一行进行处理
                '''
                if self.scan_ssh.exe_com(host=self.host, peer=str(line), report_file=self.report_file):
                    result+=1
                pos = fstream.tell()  # 每处理一行，更新坐标
                if pos == self.res.fileSize:  # 如果读到了文件末尾，跳出循环
                    break
        fstream.close()


class Resource(object):
    def __init__(self, fileName):
        self.fileName = fileName
        self.getFileSize()

    # 计算文件大小
    def getFileSize(self):
        fstream = open(self.fileName, 'r')
        fstream.seek(0, 2)  # 这里0代表文件开始，2代表文件末尾
        self.fileSize = fstream.tell()
        fstream.close()


if __name__ == '__main__':
    # 删除历史文件
    if (os.path.exists(get_root_path() + 'datas/host_peer/host.txt')):
        os.remove(get_root_path() + 'datas/host_peer/host.txt')
    if (os.path.exists(get_root_path() + 'datas/host_peer/report.txt')):
        os.remove(get_root_path() + 'datas/host_peer/report.txt')
    key = paramiko.RSAKey.from_private_key_file("/Users/huls/.ssh/id_rsa", 'hls204')
    s = ScanApi()
    s.save_host_data()
    conf_file = get_root_path() + 'datas/config/conf.ini'
    cf = ConfigIni(conf_file)
    hosts = cf.get_key('info','hosts').split(',')
    # 读取配置文件，配置文件里面可以写一些文件的信息，这样方便修改
    fileName = get_root_path() + 'datas/host_peer/host.txt'
    report_file = get_root_path() + 'datas/host_peer/report.txt'
    starttime = time.process_time()
    # 线程数
    threadNum = int(cf.get_key('info','threadNum'))
    # 文件
    res = Resource(fileName)
    threads = []
    # 初始化线程
    for i in range(threadNum):
        rdr = Reader(res, hosts[i].strip(), 'ec2-user', 22, '', key, report_file)
        threads.append(rdr)
    # 开始线程
    for i in range(threadNum):
        threads[i].start()
    # 结束线程
    for i in range(threadNum):
        threads[i].join()
    print(float(str(time.process_time())) - starttime)
    print('成功执行总数' + str(result))
    with open(report_file, 'a') as f:
        f.write('成功连接节点数：'+str(result) +'\n')
    if(result < 60):
        # 调用报警接口
        pass
