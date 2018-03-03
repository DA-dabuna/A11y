# -*- coding: utf-8 -*- #

from __future__ import print_function

from . import recorder
from multiprocessing import Process
import wave
import requests
import pycurl
import time
import random

global keywords


def get_token():
    appId = "10861825"
    apiKey = "WC6SF28VtMvTrOw7zzjOU9se"
    secretKey = "uc4RVjMvGZzrzsjAKjTVfoeoBjr0lqdM"
    auth_url = "https://openapi.baidu.com/oauth/2.0/token?grant_type=client_credentials&client_id=" + apiKey + "&client_secret=" + secretKey

    res = requests.get(auth_url)
    json_data = res.json()
    return json_data['access_token']


def dump_res(buf):
    global keywords
    json_buff = eval(buf)
    keywords = json_buff['result']
    # print(keywords)


def use_cloud(token):
    fp = wave.open('output.wav', 'r')
    nf = fp.getnframes()
    f_len = nf * 2
    audio_data = fp.readframes(nf)

    cuid = "123456"  # my phone MAC
    srv_url = 'http://vop.baidu.com/server_api' + '?cuid=' + cuid + '&token=' + token
    http_header = [
        'Content-Type: audio/pcm; rate=8000',
        'Content-Length: %d' % f_len
    ]
    print("using baidu api...")

    c = pycurl.Curl()
    c.setopt(pycurl.URL, str(srv_url))  # curl doesn't support unicode
    c.setopt(c.HTTPHEADER, http_header)  # must be list, not dict
    c.setopt(c.POST, 1)
    c.setopt(c.CONNECTTIMEOUT, 30)
    c.setopt(c.TIMEOUT, 30)
    c.setopt(c.WRITEFUNCTION, dump_res)
    c.setopt(c.POSTFIELDS, audio_data)
    c.setopt(c.POSTFIELDSIZE, f_len)
    c.perform()
    print("finished api translate.")

def user_instruction(commands):
    print(commands)


def run(name):
    global keywords
    while True:
        token = get_token()
        isOk = recorder.recorder()
        if isOk:
            use_cloud(token)    # 将用户语音信息写入 keywords 中
            user_instruction(keywords)
        else:
            pass

def start():
    p = Process(target=run,args=('recording',)) #必须加,号
    p.start()

if __name__ == '__main__':
    start()