
import os
import re
import json
import time

import gevent
from gevent.pool import Pool
from gevent import monkey
monkey.patch_all()

import requests
# pip3 install pycryptodome
from Crypto.Cipher import AES

curr_path = os.path.dirname(os.path.realpath(__file__))


class XRKJK3Video():
    def __init__(self):
        self.baseurl = 'https://xxx.com/api'
        self.videoindex = '{}/videoindex'.format(self.baseurl)
        self.videosort = '{}/videosort'.format(self.baseurl)
        self.videolist = '%s/{}' % self.videosort
        self.videdetail = '%s/videoplay/{}' % self.baseurl
        self.videoSearchHot = '{}/videoSearchHot'.format(self.baseurl)
        self.videoSearch = '%s/0' % self.videosort
        self.videoMayLike = '{}/videomaylike'.format(self.baseurl)

    def req_xrk(self, url, params=None):
        r = requests.get(url, params=params)
        print(r.url)
        data = r.json()
        if data.get('code') != 200:
            print(data.get('msg'))
            return {}
        return data

    # 主页
    def get_video_index(self):
        data = self.req_xrk(self.videoindex)
        if not data:
            return
        print(json.dumps(data, indent=4))

    # 推荐
    def get_video_may_like(self, page=1):
        data = self.req_xrk(self.videoMayLike, params={'page': page})
        if not data:
            return

        # for item in sorted(data.get('rescont').get('data'), key=lambda x: x.get('id')):
        for item in data.get('rescont').get('data'):
            # print('{} - {} - {}'.format(item.get('id'), list([ (x.get('id'), x.get('name')) for x in item.get('labls')]), item.get('title')))
            print('{} - {} - {}'.format(item.get('id'), list([x.get('name') for x in item.get('labls')]),
                                        item.get('title')))

        print('current_page: {}'.format(data.get('rescont').get('current_page')))
        print('last_page: {}'.format(data.get('rescont').get('last_page')))

    # 热门搜索
    def get_video_search_hot(self):
        data = self.req_xrk(self.videoSearchHot)
        if not data:
            return
        for item in data.get('rescont'):
            print('{} : {}'.format(item.get('title'), item.get('lists')))

    # 搜索
    def get_video_search(self, search, page=1):
        data = self.req_xrk(self.videoSearch, params={'serach': search, 'page': page})
        if not data:
            return

        # for item in sorted(data.get('rescont').get('data'), key=lambda x: x.get('id')):
        for item in data.get('rescont').get('data'):
            print('{} - {}'.format(item.get('id'), item.get('title')))

        print('current_page: {}'.format(data.get('rescont').get('current_page')))
        print('last_page: {}'.format(data.get('rescont').get('last_page')))

    # 获取所有模块
    def get_videosort(self):
        data = self.req_xrk(self.videosort)
        if not data:
            return
        with open('{}/xrk_videosort.json'.format(curr_path), 'w') as f:
            f.write(json.dumps(data, indent=4))
        # for item in sorted(data.get('rescont'), key=lambda x: x.get('order')):
        for item in data.get('rescont'):
            print('{} - {}'.format(item.get('name'), item.get('id')))

    # 获取单个模块
    def get_videolist(self, vid, page=1, orderby=None):
        # orderby : new, hot, like
        data = self.req_xrk(self.videolist.format(vid), params={'orderby': orderby, 'page': page})
        if not data:
            return

        # for item in sorted(data.get('rescont').get('data'), key=lambda x: x.get('id')):
        for item in data.get('rescont').get('data'):
            print('{} - {}'.format(item.get('id'), item.get('title')))

        print('current_page: {}'.format(data.get('rescont').get('current_page')))
        print('last_page: {}'.format(data.get('rescont').get('last_page')))

    # 获取单个视频
    def get_videoplay(self, vpid, uuid=1):
        data = self.req_xrk(self.videdetail.format(vpid), params={'uuid': uuid})
        if not data:
            return

        for k, v in data.get('rescont').items():
            print('{} - {}'.format(k, v))

        return data.get('rescont').get('videopath')

    def grant_download_ts(self, line, num, v_d_path, cryptor=None):
        print('download file - {}'.format(num))
        with open('{}/{}.ts'.format(v_d_path, num), 'wb') as f:
            if not cryptor:
                # 先下载后解密
                f.write(requests.get(line).content)
            else:
                f.write(cryptor.decrypt(requests.get(line).content))

    # 解密下载TS流
    def download_video_ts(self, vpid, d_path, is_decrypt=None):
        v_path = self.get_videoplay(vpid)
        if not v_path:
            return

        v_d_path = '{}/{}'.format(d_path, vpid)
        if not os.path.isdir(v_d_path):
            os.makedirs(v_d_path)

        r = requests.get(v_path)
        with open('{}/{}.m3u8'.format(v_d_path, vpid), 'wb') as f:
            f.write(r.content)

        key_path = re.findall('URI="(https://.*)"', r.text)[0]
        k_val = requests.get(key_path)
        # 保存key 用于解密
        with open('{}/{}.key'.format(v_d_path, vpid), 'w') as f:
            f.write(k_val.text)

        if is_decrypt == 'y':
            cryptor = AES.new(k_val.content, AES.MODE_CBC, b'0000000000000000')
        else:
            cryptor = None

        g_list = list()
        i = 1
        for line in r.text.split('\n'):
            if line.startswith('https'):
                # pool = Pool(10)
                # g = pool.spawn(self.grant_download_ts, line, i, v_d_path, cryptor)
                g = gevent.spawn(self.grant_download_ts, line, i, v_d_path, cryptor)
                g_list.append(g)
                i += 1

        gevent.joinall(g_list)


def select_func():
    show_data = {
        '1': 'get_video_search_hot',
        '2': 'get_videosort',
        '3': 'get_videolist',
        '4': 'get_video_search',
        '5': 'get_videoplay',
        '6': 'download_video_ts',
        'q': 'quit!'
    }
    for k, v in show_data.items():
        print('{} - {}'.format(k, v))

    while True:
        in_val = input('\nPlease input: ')

        if in_val not in show_data.keys():
            for k, v in show_data.items():
                print('{} - {}'.format(k, v))
            continue

        xrk = XRKJK3Video()
        s = time.ctime()

        if in_val == '1':
            xrk.get_video_search_hot()
        elif in_val == '2':
            xrk.get_videosort()
        elif in_val == '3':
            input_data = input('Input data: ') or 30
            input_page = input('Input page: ') or 1
            input_order = input('Input order: ')
            xrk.get_videolist(input_data, input_page, input_order)
        elif in_val == '4':
            input_data = input('Input data: ')
            input_page = input('Input page: ') or 1
            xrk.get_video_search(input_data, input_page)
        elif in_val == '5':
            input_data = input('Input data: ') or 1
            xrk.get_videoplay(input_data)
        elif in_val == '6':
            input_data = input('Input data: ') or 1
            input_path = input('Input path: ') or curr_path
            is_decrypt = input('Is decrypt : ')
            xrk.download_video_ts(input_data, input_path, is_decrypt)
        else:
            break

        e = time.ctime()
        print('{} - {}'.format(s, e))


if __name__ == '__main__':
    select_func()
