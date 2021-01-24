#!/usr/bin/env python
# coding:utf-8

from moviepy.editor import *
import os

if __name__ == '__main__':
    video_list = list()
    for root, dirs, files in os.walk("./res"):
        # 精准排序待优化，当前 1,10,11,...,2,21,...,3,...
        files.sort()
        for file in files:
            if file.endswith('.mp4'):
                print('file: {}'.format(file))
                filePath = os.path.join(root, file)
                video = VideoFileClip(filePath)
                video_list.append(video)

    final_clip = concatenate_videoclips(video_list)
    final_clip.to_videofile("./target.mp4", fps=24, remove_temp=False)