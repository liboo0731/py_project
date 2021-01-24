
import os

from Crypto.Cipher import AES

curr_path = os.path.dirname(os.path.realpath(__file__))


def read_video(file_path):
    with open(file_path, 'rb') as f:
        print('read: {}'.format(file_path))
        return f.read()


def write_video(file_path, f_stream, is_decrypt):
    with open(file_path, 'wb') as f:
        print('write: {}'.format(file_path))
        # 待优化，传入二进制key 值
        cryptor = AES.new(b'856f82f18d99dead', AES.MODE_CBC, b'0000000000000000')
        if is_decrypt == 'y':
            f.write(cryptor.decrypt(f_stream))
        else:
            f.write(cryptor.encrypt(f_stream))


def add_more_ts_to_mp4(video_id, is_decrypt=None):
    if not video_id:
        print('video id is not empty.')
        return

    video_path = '{}/{}'.format(curr_path, video_id)
    if not os.path.isdir(video_path):
        print('{} is not exist.'.format(video_path))
        return

    for root, dirs, files in os.walk(video_path):
        reslt_list = sorted([file for file in files if file.endswith('.ts')], key=lambda x: int(x.replace('.ts', '')))

        if is_decrypt in ('y','n'):
            for file_name in reslt_list:
                video_file = '{}/{}'.format(video_path, file_name)
                write_video(video_file, read_video(video_file), is_decrypt)

        reslt_str = '|'.join(reslt_list)
        exec = 'ffmpeg -i "concat:{}" -c copy -absf aac_adtstoasc {}.mp4'.format(reslt_str, video_id)
        print(exec)
        os.chdir(video_path)
        os.system(exec)


if __name__ == '__main__':
    video_id = input('Input ID: ')
    is_decrypt = input('Is decrypt: ')
    add_more_ts_to_mp4(video_id, is_decrypt)

