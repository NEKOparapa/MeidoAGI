import os
import librosa
import numpy as np
import json


abs_path = os.path.dirname(__file__) #获取当前文件的绝对路径，不是调用文件的绝对路径

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

    # 设置路径及文件名
    path = f"{abs_path}/cache/mouthdata.json" 

    # 将结果写入JSON文件
    with open(path, 'w') as f:
        json.dump(mouthdata, f)

    # 返回嘴部数据文件路径
    return path

