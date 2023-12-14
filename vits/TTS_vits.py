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
def voice_bert_vits2(text, id=0, format="wav", lang="auto", length=1, noise=0.667, noisew=0.8, max=50, sdp_ratio=0.2,
                     save_audio=True, save_path=None):
    fields = {
        "text": text,
        "id": str(id),
        "format": format,
        "lang": lang,
        "length": str(length),
        "noise": str(noise),
        "noisew": str(noisew),
        "max": str(max),
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


def voice_vits_streaming(text, id=0, format="wav", lang="auto", length=1, noise=0.667, noisew=0.8, max=50,
                         save_audio=True, save_path=None):
    fields = {
        "text": text,
        "id": str(id),
        "format": format,
        "lang": lang,
        "length": str(length),
        "noise": str(noise),
        "noisew": str(noisew),
        "max": str(max),
        "streaming": 'True'
    }
    boundary = '----VoiceConversionFormBoundary' + ''.join(random.sample(string.ascii_letters + string.digits, 16))

    m = MultipartEncoder(fields=fields, boundary=boundary)
    headers = {"Content-Type": m.content_type}
    url = f"{base_url}/voice"

    res = requests.post(url=url, data=m, headers=headers)
    fname = re.findall("filename=(.+)", res.headers["Content-Disposition"])[0]
    if save_path is not None:
        path = os.path.join(save_path, fname)
    else:
        path = os.path.join(absolute_path, fname)
    if save_audio:
        with open(path, "wb") as f:
            f.write(res.content)
        print(path)
        return path
    return None


def voice_vits_streaming(text, id=0, format="wav", lang="auto", length=1, noise=0.667, noisew=0.8, max=50,
                         save_path=None):
    fields = {
        "text": text,
        "id": str(id),
        "format": format,
        "lang": lang,
        "length": str(length),
        "noise": str(noise),
        "noisew": str(noisew),
        "max": str(max),
        "streaming": 'True'
    }
    boundary = '----VoiceConversionFormBoundary' + ''.join(random.sample(string.ascii_letters + string.digits, 16))

    m = MultipartEncoder(fields=fields, boundary=boundary)
    headers = {"Content-Type": m.content_type}
    url = f"{base_url}/voice"

    res = requests.post(url=url, data=m, headers=headers, stream=True)
    fname = re.findall("filename=(.+)", res.headers["Content-Disposition"])[0]
    if save_path is not None:
        path = os.path.join(save_path, fname)
    else:
        path = os.path.join(absolute_path, fname)
    audio = res.content

    def get_file_size_from_bytes(byte_data):
        file_size_offset = 4
        file_size_length = 4

        try:
            file_size_bytes = byte_data[file_size_offset:file_size_offset + file_size_length]
            file_size = int.from_bytes(file_size_bytes, byteorder='little')
            return file_size + 8
        except IndexError:
            return None

    audio = None
    p = 0
    audio_size = None
    audios = []

    for chunk in res.iter_content(chunk_size=1024):
        if audio is None:
            audio = chunk
        else:
            audio += chunk

        p += len(chunk)
        if audio_size is not None:
            if p >= audio_size:
                p = p - audio_size
                audios.append(audio[:audio_size])
                audio = audio[audio_size:]
                audio_size = get_file_size_from_bytes(audio)
        else:
            audio_size = get_file_size_from_bytes(audio)
    for i, audio in enumerate(audios):
        with open(f"{path[:-4]}-{i}.wav", "wb") as f:
            f.write(audio)

        print(f"{path[:-4]}-{i}.wav")
    return path


# 语音转换 hubert-vits
def voice_hubert_vits(upload_path, id, format="wav", length=1, noise=0.667, noisew=0.8, save_audio=True,
                      save_path=None):
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
        url = f"{base_url}/voice/hubert-vits"

        res = requests.post(url=url, data=m, headers=headers)
    fname = re.findall("filename=(.+)", res.headers["Content-Disposition"])[0]
    if save_path is not None:
        path = os.path.join(save_path, fname)
    else:
        path = os.path.join(absolute_path, fname)
    if save_audio:
        with open(path, "wb") as f:
            f.write(res.content)
        print(path)
        return path
    return None


# 维度情感模型 w2v2-vits
def voice_w2v2_vits(text, id=0, format="wav", lang="auto", length=1, noise=0.667, noisew=0.8, max=50, emotion=0,
                    save_audio=True, save_path=None):
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
    url = f"{base_url}/voice/w2v2-vits"

    res = requests.post(url=url, data=m, headers=headers)
    fname = re.findall("filename=(.+)", res.headers["Content-Disposition"])[0]
    if save_path is not None:
        path = os.path.join(save_path, fname)
    else:
        path = os.path.join(absolute_path, fname)
    if save_audio:
        with open(path, "wb") as f:
            f.write(res.content)
        print(path)
        return path
    return None


# 语音转换 同VITS模型内角色之间的音色转换
def voice_conversion(upload_path, original_id, target_id, save_audio=True, save_path=None):
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
        url = f"{base_url}/voice/conversion"

        res = requests.post(url=url, data=m, headers=headers)

    fname = re.findall("filename=(.+)", res.headers["Content-Disposition"])[0]
    if save_path is not None:
        path = os.path.join(save_path, fname)
    else:
        path = os.path.join(absolute_path, fname)

    if save_audio:
        with open(path, "wb") as f:
            f.write(res.content)
        print(path)
        return path
    return None


def voice_ssml(ssml, save_audio=True, save_path=None):
    fields = {
        "ssml": ssml,
    }
    boundary = '----VoiceConversionFormBoundary' + ''.join(random.sample(string.ascii_letters + string.digits, 16))

    m = MultipartEncoder(fields=fields, boundary=boundary)
    headers = {"Content-Type": m.content_type}
    url = f"{base_url}/voice/ssml"

    res = requests.post(url=url, data=m, headers=headers)
    fname = re.findall("filename=(.+)", res.headers["Content-Disposition"])[0]
    if save_path is not None:
        path = os.path.join(save_path, fname)
    else:
        path = os.path.join(absolute_path, fname)

    if save_audio:
        with open(path, "wb") as f:
            f.write(res.content)
        print(path)
        return path
    return None


def voice_dimensional_emotion(upload_path, save_audio=True,
                              save_path=None):
    upload_name = os.path.basename(upload_path)
    upload_type = f'audio/{upload_name.split(".")[1]}'  # wav,ogg

    with open(upload_path, 'rb') as upload_file:
        fields = {
            "upload": (upload_name, upload_file, upload_type),
        }
        boundary = '----VoiceConversionFormBoundary' + ''.join(random.sample(string.ascii_letters + string.digits, 16))

        m = MultipartEncoder(fields=fields, boundary=boundary)
        headers = {"Content-Type": m.content_type}
        url = f"{base_url}/voice/dimension-emotion"

        res = requests.post(url=url, data=m, headers=headers)
    fname = re.findall("filename=(.+)", res.headers["Content-Disposition"])[0]
    if save_path is not None:
        path = os.path.join(save_path, fname)
    else:
        path = os.path.join(absolute_path, fname)
    if save_audio:
        with open(path, "wb") as f:
            f.write(res.content)
        print(path)
        return path
    return None


def vits_json(text, id=0, format="wav", lang="auto", length=1, noise=0.667, noisew=0.8, max=50,
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
    f = json.dumps(fields)
    url = f"{base_url}/voice"
    header = {"Content-Type": 'application/json'}
    res = requests.post(url=url, data=f, headers=header)

    fname = re.findall("filename=(.+)", res.headers["Content-Disposition"])[0]
    if save_path is not None:
        path = os.path.join(save_path, fname)
    else:
        path = os.path.join(absolute_path, fname)

    with open(path, "wb") as f:
        f.write(res.content)
    print(path)
    return path



def test_interface(text):
    error_num = 0
    for i in range(100):
        try:
            time.sleep(1)
            t1 = time.time()
            voice_vits(text, format="wav", lang="zh", save_audio=False)
            t2 = time.time()
            print(f"{i}:len:{len(text)}耗时:{t2 - t1}")
        except Exception as e:
            error_num += 1
            print(e)
    print(f"error_num={error_num}")

