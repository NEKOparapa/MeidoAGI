import re
import requests
import os
import random
import string
from requests_toolbelt.multipart.encoder import MultipartEncoder  #需要安装requests_toolbelt

abs_path = os.path.dirname(__file__) #获取当前文件的绝对路径，不是调用文件的绝对路径
base = "http://127.0.0.1:23456"


# 映射表
def voice_speakers():
    url = f"{base}/voice/speakers"

    res = requests.post(url=url)
    json = res.json()
    for i in json:
        print(i)
        for j in json[i]:
            print(j)
    return json


# 语音合成 voice vits
def voice_vits(text, id=0, format="wav", lang="auto", length=1, noise=0.667, noisew=0.8, max=50):
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
    url = f"{base}/voice"

    res = requests.post(url=url, data=m, headers=headers)
    #修改为固定文件名
    #fname = re.findall("filename=(.+)", res.headers["Content-Disposition"])[0]
    fname = "voice.wav"
    path = f"{abs_path}/cache/{fname}" 

    with open(path, "wb") as f:
        f.write(res.content)
    #print('语音存储位置：',path)

    return path


# 语音转换 hubert-vits
def voice_hubert_vits(upload_path, id, format="wav", length=1, noise=0.667, noisew=0.8):
    upload_name = os.path.basename(upload_path)
    upload_type = f'audio/{upload_name.split(".")[1]}'  # wav,ogg

    with open(upload_path, 'rb') as upload_file:
        fields = {
            "upload": (upload_name, upload_file, upload_type),
            "id": str(id),
            "format": format,
            "length": str(length),
            "noise": str(noise),
            "noisew": str(noisew),
        }
        boundary = '----VoiceConversionFormBoundary' + ''.join(random.sample(string.ascii_letters + string.digits, 16))

        m = MultipartEncoder(fields=fields, boundary=boundary)
        headers = {"Content-Type": m.content_type}
        url = f"{base}/voice/hubert-vits"

        res = requests.post(url=url, data=m, headers=headers)
    fname = re.findall("filename=(.+)", res.headers["Content-Disposition"])[0]
    path = f"{abs_path}/{fname}"

    with open(path, "wb") as f:
        f.write(res.content)
    print(path)
    return path


# 维度情感模型 w2v2-vits
def voice_w2v2_vits(text, id=0, format="wav", lang="auto", length=1, noise=0.667, noisew=0.8, max=50, emotion=0):
    fields = {
        "text": text,
        "id": str(id),
        "format": format,
        "lang": lang,
        "length": str(length),
        "noise": str(noise),
        "noisew": str(noisew),
        "max": str(max),
        "emotion": str(emotion)
    }
    boundary = '----VoiceConversionFormBoundary' + ''.join(random.sample(string.ascii_letters + string.digits, 16))

    m = MultipartEncoder(fields=fields, boundary=boundary)
    headers = {"Content-Type": m.content_type}
    url = f"{base}/voice/w2v2-vits"

    res = requests.post(url=url, data=m, headers=headers)
    fname = re.findall("filename=(.+)", res.headers["Content-Disposition"])[0]
    path = f"{abs_path}/{fname}"

    with open(path, "wb") as f:
        f.write(res.content)
    print(path)
    return path


# 语音转换 同VITS模型内角色之间的音色转换
def voice_conversion(upload_path, original_id, target_id):
    upload_name = os.path.basename(upload_path)
    upload_type = f'audio/{upload_name.split(".")[1]}'  # wav,ogg

    with open(upload_path, 'rb') as upload_file:
        fields = {
            "upload": (upload_name, upload_file, upload_type),
            "original_id": str(original_id),
            "target_id": str(target_id),
        }
        boundary = '----VoiceConversionFormBoundary' + ''.join(random.sample(string.ascii_letters + string.digits, 16))
        m = MultipartEncoder(fields=fields, boundary=boundary)

        headers = {"Content-Type": m.content_type}
        url = f"{base}/voice/conversion"

        res = requests.post(url=url, data=m, headers=headers)

    fname = re.findall("filename=(.+)", res.headers["Content-Disposition"])[0]
    path = f"{abs_path}/{fname}"

    with open(path, "wb") as f:
        f.write(res.content)
    print(path)
    return path


def voice_ssml(ssml):
    fields = {
        "ssml": ssml,
    }
    boundary = '----VoiceConversionFormBoundary' + ''.join(random.sample(string.ascii_letters + string.digits, 16))

    m = MultipartEncoder(fields=fields, boundary=boundary)
    headers = {"Content-Type": m.content_type}
    url = f"{base}/voice/ssml"

    res = requests.post(url=url, data=m, headers=headers)
    fname = re.findall("filename=(.+)", res.headers["Content-Disposition"])[0]
    path = f"{abs_path}/{fname}"

    with open(path, "wb") as f:
        f.write(res.content)
    print(path)
    return path

def voice_dimensional_emotion(upload_path):
    upload_name = os.path.basename(upload_path)
    upload_type = f'audio/{upload_name.split(".")[1]}'  # wav,ogg

    with open(upload_path, 'rb') as upload_file:
        fields = {
            "upload": (upload_name, upload_file, upload_type),
        }
        boundary = '----VoiceConversionFormBoundary' + ''.join(random.sample(string.ascii_letters + string.digits, 16))

        m = MultipartEncoder(fields=fields, boundary=boundary)
        headers = {"Content-Type": m.content_type}
        url = f"{base}/voice/dimension-emotion"

        res = requests.post(url=url, data=m, headers=headers)
    fname = re.findall("filename=(.+)", res.headers["Content-Disposition"])[0]
    path = f"{abs_path}/{fname}"

    with open(path, "wb") as f:
        f.write(res.content)
    print(path)
    return path


