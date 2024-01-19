import json
import re
import requests
import os
import time
import random
import string
from requests_toolbelt.multipart.encoder import MultipartEncoder

absolute_path = os.path.dirname(__file__)#获取当前文件的绝对路径，不是调用文件的绝对路径
base_url = "http://127.0.0.1:23456"


# 映射表
def voice_speakers():
    url = f"{base_url}/voice/speakers"

    res = requests.post(url=url)
    json = res.json()
    for i in json:
        print(i)
        for j in json[i]:
            print(j)
    return json


# 语音合成 voice vits
def voice_vits(text, id=0, format="wav", lang="auto", length=1, noise=0.667, noisew=0.8, max=50, save_audio=True,
               save_path=None):
    fields = {
        "text": text,
        "id": str(id),
        "format": format,
        "lang": lang,
        "length": str(length),
        "noise": str(noise),
        "noisew": str(noisew),
        "max": str(max)
    }
    boundary = '----VoiceConversionFormBoundary' + ''.join(random.sample(string.ascii_letters + string.digits, 16))

    m = MultipartEncoder(fields=fields, boundary=boundary)
    headers = {"Content-Type": m.content_type}
    url = f"{base_url}/voice/vits"

    res = requests.post(url=url, data=m, headers=headers)
    #fname = re.findall("filename=(.+)", res.headers["Content-Disposition"])[0]
    #修改为固定文件名
    fname = "voice.wav"


    if save_path is not None:
        path = os.path.join(save_path, fname)
    else:
        path =f"{absolute_path}/cache/{fname}" 
    if save_audio:
        with open(path, "wb") as f:
            f.write(res.content)
        #print(path)
        print('[DEBUG] 已生成语音存储位置：',path)
        return path
    return None



# Bert_vits2
def voice_bert_vits2(text, id=0, format="wav", lang="auto", length=1, noise=0.667, noisew=0.8, segment_size=50, sdp_ratio=0.2,
                     save_audio=True, save_path=None):
    fields = {
        "text": text,
        "id": str(id),
        "format": format,
        "lang": lang,
        "length": str(length),
        "noise": str(noise),
        "noisew": str(noisew),
        "segment_size": str(segment_size),
        "sdp_ratio": str(sdp_ratio)
    }
    boundary = '----VoiceConversionFormBoundary' + ''.join(random.sample(string.ascii_letters + string.digits, 16))

    m = MultipartEncoder(fields=fields, boundary=boundary)
    headers = {"Content-Type": m.content_type}
    url = f"{base_url}/voice/bert-vits2"

    res = requests.post(url=url, data=m, headers=headers)

    #fname = re.findall("filename=(.+)", res.headers["Content-Disposition"])[0]
    #修改为固定文件名
    fname = "voice.wav"

    if save_path is not None:
        path = os.path.join(save_path, fname)
    else:
        path = f"{absolute_path}/cache/{fname}" 
    if save_audio:
        with open(path, "wb") as f:
            f.write(res.content)
        print('[DEBUG] 已生成语音存储位置：',path)
        return path
    return None




