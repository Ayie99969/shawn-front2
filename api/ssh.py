import datetime

import paramiko


class SSHConnect:
    def __init__(self, host='', username='', port=22, password='', key = None):
        self.ip = host
        self.port = port
        self.username = username
        self.password = password
        self.connection = None
        self.key = key

    def connect(self):
        self.connection = paramiko.SSHClient()
        self.connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            if self.password != '':
                self.connection.connect(self.ip, self.port, self.username, (str(self.password)), timeout=5.0)
            else:
                try:
                    # 连接服务器
                    self.connection.connect(self.ip, self.port, self.username, pkey=self.key, timeout=5.0)
                except paramiko.ssh_exception.SSHException:
                    self.connection.get_transport().auth_none(self.username)
                    self.connection.exec_command('uname -a')
                self.connection.sftp = paramiko.SFTPClient.from_transport(self.connection.get_transport())
        except Exception as e:
            try:
                print(str(e.args))
                self.connection = None
            finally:
                e = None
                del e

    def exe_com(self, host, peer, report_file):
        flag = False
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # 执行命令并获取命令结果
        stdin, stdout, stderr = self.connection.exec_command('export BTFS_PATH=~/monitor/node/.btfs;~/monitor/btfs/btfs swarm connect /p2p/'+peer)
        # 打印结果
        for line in stdout.readlines():
            print('执行line：' + line.strip())
            with open(report_file, 'a') as f:
                f.write(now_time + ' host: ' + host + ' result：' + line.strip() + '\n')
                if ('success' in str(line.strip())):
                    flag = True
            f.close()
            return flag
