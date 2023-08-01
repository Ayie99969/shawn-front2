import json

import paramiko
import requests

from common.utils import get_root_path, save_export_to_txt, save_host_to_txt

class ScanApi:

    def __init__(self):
        self.scan_url = "https://scan-backend.btfs.io"
        self.num = 0
    # 请求外部服务
    def get_scan_top(self):
        #获取scan top100的节点信息
        payload = json.dumps({
            "rank_flag": 2,
            "limit": 100,
            "start": 0
        })
        headers = {
            'User-Agent': 'Apifox/1.0.0 (https://www.apifox.cn)',
            'Content-Type': 'application/json'
        }
        res = requests.request("POST", self.scan_url + "/api/node/v2/btfsscan/rank", headers=headers, data=payload)
        if res.status_code == 200:
            return res.json()
        else:
            print(res.status_code)

    # 节点数据写入txt文件
    def save_host_data(self):
        res = self.get_scan_top()
        save_host_to_txt(res, filename='host.txt')


if __name__ == '__main__':
    s = ScanApi()
    s.save_host_data()
    hosts = ['54.177.62.240','54.193.204.37','54.151.102.54']
    # s.save_host_data()
    # s.ssh_host_exe_peer("54.177.62.240", 22 , "ec2-user",'16Uiu2HAm5HCYgEqXzjJptywGS8CsXq6no7r18NuYsfiLEV8vzPAo')
