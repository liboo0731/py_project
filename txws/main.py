#!/usr/bin/env python
# coding:utf-8

import os
import re
import requests
import random


class TXWS():
    headers = {
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1 Edg/84.0.4147.105'
    }

    def __init__(self, s_url):
        self.url = re.findall('(https?://[^\s]+)', s_url)[0]
        self.data = {
            'datalvl': "all",
            'feedid': str(self.url).split('/')[5],
            'recommendtype': '0',
            '_weishi_mapExt': '{}'
        }

    def txws_download(self):
        url = 'https://h5.weishi.qq.com/webapp/json/weishi/WSH5GetPlayPage?t={}&g_tk='.format(random.random())
        # r = requests.post(url, proxies=proxy, headers=self.headers, data=self.data)
        r = requests.post(url, headers=self.headers, data=self.data)
        video_name = r.json()['data']['feeds'][0]['feed_desc'].replace(' ', '')
        if video_name == '':
            video_name = int(random.random() * 2 * 1000)
        if len(str(video_name)) > 20:
            video_name = video_name[:20]
        video_url = r.json()['data']['feeds'][0]['video_url']
        # video = requests.get(video_url, proxies=proxy, headers=self.headers).content
        video = requests.get(video_url, headers=self.headers).content
        video_local_path = '{}/{}.mp4'.format(os.path.dirname(os.path.realpath(__file__)), video_name)
        with open(video_local_path, 'wb') as f:
            f.write(video)
        print("{}.mp4 download success!".format(video_name))


if __name__ == '__main__':
    org_url = input('Input link: ')
    TXWS(org_url).txws_download()
