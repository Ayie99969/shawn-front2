# 创建txt文件
import datetime
import os

# 节点写入txt文件
def save_host_to_txt(scan_json ,  filename):
    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # datafile = get_root_path() + 'datas/host_peer/' + now_time + '_host.txt'
    datafile = get_root_path() + 'datas/host_peer/'+ filename
    file_handle = open(datafile, mode='w')
    node_info = scan_json['data']
    node_num = len(node_info)
    for i in range(node_num):
        host_pid = node_info[i]['host_pid']
        file_handle.write(host_pid +'\n')
    file_handle.close()

# 报告写入txt文件
def save_export_to_txt(export_list ,  filename):
    datafile = get_root_path() + 'datas/host_peer/'+ filename
    file_handle = open(datafile, 'a', encoding='utf-8')
    for i in range(len(export_list)):
        export_data = str(export_list[i])
        file_handle.write(export_data + '\n')
    file_handle.close()


# 获取项目目录
def get_root_path():
    p_name = "scan_host_project"
    # os.path.abspath(os.path.dirname(__file__)) 返回当前文件的绝对路径
    project_path = os.path.abspath(os.path.dirname(__file__))
    if project_path.find('/') != -1: separator = '/'
    root_path = project_path[:project_path.find(f'{p_name}{separator}') + len(f'{p_name}{separator}')]
    return root_path

