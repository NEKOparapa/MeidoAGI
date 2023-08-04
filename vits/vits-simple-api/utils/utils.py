import logging
import os
from json import loads
from torch import load, FloatTensor
from numpy import float32
import librosa


class HParams():
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if type(v) == dict:
                v = HParams(**v)
            self[k] = v

    def keys(self):
        return self.__dict__.keys()

    def items(self):
        return self.__dict__.items()

    def values(self):
        return self.__dict__.values()

    def __len__(self):
        return len(self.__dict__)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    def __contains__(self, key):
        return key in self.__dict__

    def __repr__(self):
        return self.__dict__.__repr__()


def load_checkpoint(checkpoint_path, model):
    checkpoint_dict = load(checkpoint_path, map_location='cpu')
    iteration = checkpoint_dict.get('iteration', None)
    saved_state_dict = checkpoint_dict['model']
    if hasattr(model, 'module'):
        state_dict = model.module.state_dict()
    else:
        state_dict = model.state_dict()
    new_state_dict = {}
    for k, v in state_dict.items():
        try:
            new_state_dict[k] = saved_state_dict[k]
        except:
            logging.info(f"{k} is not in the checkpoint")
            new_state_dict[k] = v
    if hasattr(model, 'module'):
        model.module.load_state_dict(new_state_dict)
    else:
        model.load_state_dict(new_state_dict)
    if iteration:
        logging.info(f"Loaded checkpoint '{checkpoint_path}' (iteration {iteration})")
    else:
        logging.info(f"Loaded checkpoint '{checkpoint_path}'")
    return


def get_hparams_from_file(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        data = f.read()
    config = loads(data)

    hparams = HParams(**config)
    return hparams


def load_audio_to_torch(full_path, target_sampling_rate):
    audio, sampling_rate = librosa.load(full_path, sr=target_sampling_rate, mono=True)
    return FloatTensor(audio.astype(float32))


def clean_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        # 如果是文件，则删除文件
        if os.path.isfile(file_path):
            os.remove(file_path)


# is none -> True, is not none -> False
def check_is_none(s):
    return s is None or (isinstance(s, str) and str(s).isspace()) or str(s) == ""

def save_audio(audio, path):
    with open(path,"wb") as f:
        f.write(audio)
