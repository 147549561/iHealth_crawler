#coding=utf8
import re
import sys
import socket
import requests
from datetime import datetime
from lxml import etree

from ProxyIP import ProxyIP

# 实例化代理池对象，全局使用，最多实例化进程个数次，防止冗余的实例化
proxyip = ProxyIP()
# 设置最大尝试次数
requests.adapters.DEFAULT_RETRIES = 1
# 请求超时时间
timeout = 5

# 设置
watch_interval = 1 * 60 * 60                # 默认监控时间间隔，单位为秒

# 数据库配置
mongo_dbname = 'iHealth'
mongo_host = '123.56.8.91'          # mongodb 主机地址
mongo_port = 27017                  # mongodb 主机端口
mongo_user = 'admin'                # mongodb 登陆用户
mongo_pwd  = 'admin123'             # mongodb 用户密码

# 编码信息
input_encoding = sys.stdin.encoding
output_encoding = sys.stdout.encoding
file_encoding = 'utf8'



def printx(s, end = '\n'):
    '''通用输出'''
    '''可输出 str、dict 类型'''
    '''可自动转换编码'''
    if output_encoding == None:
        sys.stdout.write(s)
        sys.stdout.write('\n')
    elif isinstance(s,str):
        s = s.decode(file_encoding)
        s += end
        s = s.encode(output_encoding)
        sys.stdout.write(s)
    elif isinstance(s,dict):
        s = json.dumps(s, indent=4, ensure_ascii=False)
        s += end
        s = s.encode(output_encoding)
        sys.stdout.write(s)
    else:
        print s
    sys.stdout.flush()

def Parse(url,pattern):
    # 根据模式串 pattern 解析 url 页面源码（XPATH）
    # 设置代理IP，发送请求
    while True:
        try:
            ip = proxyip.get()
            proxies = {'https':'%s:%d'%(ip[0],ip[1])}
            response = requests.get(url, proxies=proxies, timeout=timeout)
            break
        except Exception,e:
            printx('请求失败，重试')
    # 解析
    selector = etree.HTML(response.content)
    items = selector.xpath(pattern)
    return items

def Parse_re(url,pattern):
    # 根据模式串 pattern 解析 url 页面源码（正则匹配）
    # 设置代理IP，发送请求
    while True:
        try:
            ip = proxyip.get()
            proxies = {'https':'%s:%d'%(ip[0],ip[1])}
            response = requests.get(url, proxies=proxies, timeout=timeout)
            break
        except Exception,e:
            printx('请求失败，重试')
    # 解析
    html = response.content
    pattern = re.compile(pattern,re.S)
    items = re.findall(pattern,html)
    return items

def getLivePageSum(key):
    # 获取某关键字的直播间总页数
    url = 'https://search.bilibili.com/live?keyword=%s'%key.decode('utf8')
    LivePageSum_pattern = r'data-num_pages="(.*?)"'

    # 匹配直播间总数
    try:
        items = Parse(url, LivePageSum_pattern)
        return int(items[0])
    except Exception,e:
        raise Exception,'获取某关键字的直播间总页数失败'

def getCurLiveNo(key,page):
    # 获取当前页面的直播间列表
    url = 'https://search.bilibili.com/live?keyword=%s&page=%d&type=all&order=online&coverType=user_cover'%(key.decode('utf8'),page)
    LiveNo_pattern = r'<li class="room-item">.*?live\.bilibili\.com/(.*?)\?.*?<i class="icon-live-watch"></i><span>(.*?)</span>'

    # 匹配当前页面的所有直播间号
    items = Parse(url, LiveNo_pattern)
    # if len(items) == 0:
    #     raise Exception,'获取第 %d 页直播间列表失败'%page
    return items
