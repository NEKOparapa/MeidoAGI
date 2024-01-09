import os
import librosa
import numpy as np
import json
import http.client
import requests
import random
import string
from requests_toolbelt.multipart.encoder import MultipartEncoder
import threading
import time
from datetime import datetime

absolute_path = os.path.dirname(__file__)#获取当前脚本文件的绝对路径，不是调用文件的绝对路径
base_url = "http://127.0.0.1:23456"



function_timed_voice_notification  = {
        "type": "function",
        "function": {
                    "name": "timed_voice_notification",
                    "description": "输入通知的日期时间与通知内容，会在该时间进行语音通知到用户",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "target_datetime": {
                                "type": "string",
                                "description": "输入通知的日期时间，例如：2023-12-18 19:44:00，无法输入例如“5 minutes later”",
                                "enum": ["2023-12-01 00:00:00 —— 2030-12-12 12:12:00"], 
                            },
                            "text": {
                                "type": "string",
                                "description": "输入通知的内容",
                            }
                        },
                        "required": ["target_datetime","text"]
                    },
                }
}


#定时发送语音通知的函数
def timed_voice_notification(target_datetime,text):
    try:
        # 将输入的日期时间字符串转换为 datetime 对象
        target_datetime = datetime.strptime(target_datetime, "%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        print(f"输入的日期时间格式错误：{e}")
        return "输入的日期时间格式错误"

    # 创建子线程并启动
    thread = threading.Thread(target=countdown_task, args=(target_datetime,text,), daemon=True)
    thread.start()

    # 等待子线程执行完毕
    #thread.join()
    
    print (f"已经成功创建定时语音通知任务，将会在{target_datetime}进行通知")
    return f"已经成功创建定时语音通知任务，将会在{target_datetime}进行通知"

#检查系统时间与目标时间的函数
def countdown_task(target_datetime,text):
    """
    子线程任务：倒计时，直到系统时间超过目标日期时间。
    """
    target_time = target_datetime.timestamp()

    while time.time() < target_time:
        remaining_time = target_time - time.time()
        #print(f"子线程：距离目标时间还有 {remaining_time:.2f} 秒")
        time.sleep(1)

    send_voice_notification(text)
    #print("子线程：任务完成")


#发送日常任务执行结果通知的函数
def send_voice_notification(text):

    #构建任务结果通知语句
    content =  f"主人，您的定时通知：{text}。"


    # 生成 AI 回复的语音
    audio_path = voice_bert_vits2(text=content)

    # 生成语音的口型数据文件
    mouth_data_path = convertAudioToMouthData(audio_path)

    data = {
        "assistant_audio_path": audio_path,
        "assistant_mouth_data_path": mouth_data_path,
        "assistant_response_text": content
    }

    # 将数据转换为 JSON 字符串
    json_data = json.dumps(data)

    # 设置请求头
    headers = {
        'Content-Type': 'application/json',
        'Content-Length': len(json_data)
    }

    # 发送 POST 请求
    conn = http.client.HTTPConnection('localhost', 4000)
    conn.request('POST', '/notification', json_data, headers)

    # 获取响应
    response = conn.getresponse()

    # 打印响应结果
    #print('Response Status:', response.status)
    #print('Response Body:', response.read().decode())

    # 关闭连接
    conn.close()


# 将音频文件转换为嘴部数据
def convertAudioToMouthData(audio_path):

    # 加载音频文件
    y, sr = librosa.load(audio_path)

    # 计算每个0.1秒的响度
    hop_length = int(0.1 * sr) # 0.1秒的样本数量
    rmse = librosa.feature.rms(y=y, frame_length=hop_length, hop_length=hop_length)

    # 计算平均响度
    avg_rmse = np.mean(rmse)

    # 将响度值转换为分贝，参考点设置为平均响度
    loudness_db = librosa.amplitude_to_db(rmse, ref=avg_rmse)

    # 压平数组
    loudness_db_flattened = loudness_db.flatten()

    # 将分贝值归一化到 0-1
    loudness_normalized = (loudness_db_flattened - np.min(loudness_db_flattened)) / (np.max(loudness_db_flattened) - np.min(loudness_db_flattened))

    # 由于NumPy数组不能直接序列化为JSON，我们需要将其转换为普通的Python列表
    mouthdata = loudness_normalized.tolist()

    #缩小一下数值
    mouthdata = [x * 0.6 for x in mouthdata]

    # 设置路径及文件名
    path = f"{absolute_path}/cache/mouthdata.json" 
    print('[DEBUG] 已生成口型数据存储位置：',path,'\n')

    # 将结果写入JSON文件
    with open(path, 'w') as f:
        json.dump(mouthdata, f)

    # 返回嘴部数据文件路径
    return path


# Bert_vits2的语音生成
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

#测试用
#timed_voice_notification(target_datetime_str = "2023-12-18 19:44:00",text="你该出门走走了，大猪头")