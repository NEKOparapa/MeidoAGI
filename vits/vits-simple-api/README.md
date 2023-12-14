<div class="title" align=center>
    <h1>vits-simple-api</h1>
	<div>Simply call the vits api</div>
    <br/>
    <br/>
    <p>
        <img src="https://img.shields.io/github/license/Artrajz/vits-simple-api">
    	<img src="https://img.shields.io/badge/python-3.10-green">
        <a href="https://hub.docker.com/r/artrajz/vits-simple-api">
            <img src="https://img.shields.io/docker/pulls/artrajz/vits-simple-api"></a>
    </p>
    <a href="https://github.com/Artrajz/vits-simple-api/blob/main/README.md">English</a>|<a href="https://github.com/Artrajz/vits-simple-api/blob/main/README_zh.md">中文文档</a>
    <br/>
</div>





# Feature

- [x] VITS text-to-speech, voice conversion
- [x] HuBert-soft VITS
- [x] [vits_chinese](https://github.com/PlayVoice/vits_chinese)
- [x] [Bert-VITS2](https://github.com/Stardust-minus/Bert-VITS2)
- [x] W2V2 VITS / [emotional-vits](https://github.com/innnky/emotional-vits) dimensional emotion model
- [x] Support for loading multiple models
- [x] Automatic language recognition and processing,set the scope of language type recognition according to model's cleaner,support for custom language type range
- [x] Customize default parameters
- [x] Long text batch processing
- [x] GPU accelerated inference
- [x] SSML (Speech Synthesis Markup Language) work in progress...


## demo

[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/Artrajz/vits-simple-api)

Please note that different IDs may support different languages.[speakers](https://artrajz-vits-simple-api.hf.space/voice/speakers)

- `https://artrajz-vits-simple-api.hf.space/voice/vits?text=你好,こんにちは&id=164`
- `https://artrajz-vits-simple-api.hf.space/voice/vits?text=Difficult the first time, easy the second.&id=4`
- excited:`https://artrajz-vits-simple-api.hf.space/voice/w2v2-vits?text=こんにちは&id=3&emotion=111`
- whispered:`https://artrajz-vits-simple-api.hf.space/w2v2-vits?text=こんにちは&id=3&emotion=2077` 

https://user-images.githubusercontent.com/73542220/237995061-c1f25b4e-dd86-438a-9363-4bb1fe65b425.mov

# Deploy

## Docker(Recommended for Linux)

### Docker image pull script

```
bash -c "$(wget -O- https://raw.githubusercontent.com/Artrajz/vits-simple-api/main/vits-simple-api-installer-latest.sh)"
```

- The platforms currently supported by Docker images are `linux/amd64` and `linux/arm64`.(arm64 only has a CPU version)
- After a successful pull, the vits model needs to be imported before use. Please follow the steps below to import the model.

### Download  VITS model

Put the model into `/usr/local/vits-simple-api/Model`

<details><summary>Folder structure</summary><pre><code>
│  hubert-soft-0d54a1f4.pt
│  model.onnx
│  model.yaml
│
├─g
│      config.json
│      G_953000.pth
│
├─louise
│      360_epochs.pth
│      config.json
│
├─Nene_Nanami_Rong_Tang
│      1374_epochs.pth
│      config.json
│
├─Zero_no_tsukaima
│       1158_epochs.pth
│       config.json
│
└─npy
       25ecb3f6-f968-11ed-b094-e0d4e84af078.npy
       all_emotions.npy
</code></pre></details>





### Modify model path

Modify in  `/usr/local/vits-simple-api/config.py` 

<details><summary>config.py</summary><pre><code>
# Fill in the model path here
MODEL_LIST = [
    # VITS
    [ABS_PATH + "/Model/Nene_Nanami_Rong_Tang/1374_epochs.pth", ABS_PATH + "/Model/Nene_Nanami_Rong_Tang/config.json"],
    [ABS_PATH + "/Model/Zero_no_tsukaima/1158_epochs.pth", ABS_PATH + "/Model/Zero_no_tsukaima/config.json"],
    [ABS_PATH + "/Model/g/G_953000.pth", ABS_PATH + "/Model/g/config.json"],
    # HuBert-VITS (Need to configure HUBERT_SOFT_MODEL)
    [ABS_PATH + "/Model/louise/360_epochs.pth", ABS_PATH + "/Model/louise/config.json"],
    # W2V2-VITS (Need to configure DIMENSIONAL_EMOTION_NPY)
    [ABS_PATH + "/Model/w2v2-vits/1026_epochs.pth", ABS_PATH + "/Model/w2v2-vits/config.json"],
]
# hubert-vits: hubert soft model
HUBERT_SOFT_MODEL = ABS_PATH + "/Model/hubert-soft-0d54a1f4.pt"
# w2v2-vits: Dimensional emotion npy file
# load single npy: ABS_PATH+"/all_emotions.npy
# load mutiple npy: [ABS_PATH + "/emotions1.npy", ABS_PATH + "/emotions2.npy"]
# load mutiple npy from folder: ABS_PATH + "/Model/npy"
DIMENSIONAL_EMOTION_NPY = ABS_PATH + "/Model/npy"
# w2v2-vits: Need to have both `model.onnx` and `model.yaml` files in the same path.
DIMENSIONAL_EMOTION_MODEL = ABS_PATH + "/Model/model.yaml"
</code></pre></details>





### Startup

`docker compose up -d`

Or execute the pull script again

### Image update 

Run the docker image pull script again 

## Virtual environment deployment

### Clone

`git clone https://github.com/Artrajz/vits-simple-api.git`

###  Download python dependencies 

A python virtual environment is recommended

`pip install -r requirements.txt`

Fasttext may not be installed on windows, you can install it with the following command,or download wheels [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#fasttext)

```
# python3.10 win_amd64
pip install https://github.com/Artrajz/archived/raw/main/fasttext/fasttext-0.9.2-cp310-cp310-win_amd64.whl
```

### Download  VITS model 

Put the model into `/path/to/vits-simple-api/Model`

<details><summary>Folder structure</summary><pre><code>
│  hubert-soft-0d54a1f4.pt
│  model.onnx
│  model.yaml
│
├─g
│      config.json
│      G_953000.pth
│
├─louise
│      360_epochs.pth
│      config.json
│
├─Nene_Nanami_Rong_Tang
│      1374_epochs.pth
│      config.json
│
├─Zero_no_tsukaima
│       1158_epochs.pth
│       config.json
│
└─npy
       25ecb3f6-f968-11ed-b094-e0d4e84af078.npy
       all_emotions.npy
</code></pre></details>



### Modify model path

Modify in  `/path/to/vits-simple-api/config.py` 

<details><summary>config.py</summary><pre><code>
# Fill in the model path here
MODEL_LIST = [
    # VITS
    [ABS_PATH + "/Model/Nene_Nanami_Rong_Tang/1374_epochs.pth", ABS_PATH + "/Model/Nene_Nanami_Rong_Tang/config.json"],
    [ABS_PATH + "/Model/Zero_no_tsukaima/1158_epochs.pth", ABS_PATH + "/Model/Zero_no_tsukaima/config.json"],
    [ABS_PATH + "/Model/g/G_953000.pth", ABS_PATH + "/Model/g/config.json"],
    # HuBert-VITS (Need to configure HUBERT_SOFT_MODEL)
    [ABS_PATH + "/Model/louise/360_epochs.pth", ABS_PATH + "/Model/louise/config.json"],
    # W2V2-VITS (Need to configure DIMENSIONAL_EMOTION_NPY)
    [ABS_PATH + "/Model/w2v2-vits/1026_epochs.pth", ABS_PATH + "/Model/w2v2-vits/config.json"],
]
# hubert-vits: hubert soft model
HUBERT_SOFT_MODEL = ABS_PATH + "/Model/hubert-soft-0d54a1f4.pt"
# w2v2-vits: Dimensional emotion npy file
# load single npy: ABS_PATH+"/all_emotions.npy
# load mutiple npy: [ABS_PATH + "/emotions1.npy", ABS_PATH + "/emotions2.npy"]
# load mutiple npy from folder: ABS_PATH + "/Model/npy"
DIMENSIONAL_EMOTION_NPY = ABS_PATH + "/Model/npy"
# w2v2-vits: Need to have both `model.onnx` and `model.yaml` files in the same path.
DIMENSIONAL_EMOTION_MODEL = ABS_PATH + "/Model/model.yaml"
</code></pre></details>



### Startup

`python app.py`

# GPU accelerated

## Windows
### Install CUDA
Check the highest version of CUDA supported by your graphics card:
```
nvidia-smi
```
Taking CUDA 11.7 as an example, download it from the [official website](https://developer.nvidia.com/cuda-11-7-0-download-archive?target_os=Windows&amp;target_arch=x86_64&amp;target_version=10&amp;target_type=exe_local)
### Install GPU version of PyTorch

1.13.1+cu117 is recommended, other versions may have memory instability issues.

```
pip install torch==1.13.1+cu117 --extra-index-url https://download.pytorch.org/whl/cu117
```
## Linux
The installation process is similar, but I don't have the environment to test it.

# Dependency Installation Issues

Since pypi.org does not have the `pyopenjtalk` whl file, it usually needs to be installed from the source code. This process might be troublesome for some people. Therefore, you can also use the whl I built for installation.

```
pip install pyopenjtalk -i https://pypi.artrajz.cn/simple
```

# API

## GET

#### speakers list 

- GET http://127.0.0.1:23456/voice/speakers

  Returns the mapping table of role IDs to speaker names.

#### voice vits

- GET http://127.0.0.1:23456/voice/vits?text=text

  Default values are used when other parameters are not specified.

- GET http://127.0.0.1:23456/voice/vits?text=[ZH]text[ZH][JA]text[JA]&lang=mix

  When lang=mix, the text needs to be annotated.

- GET http://127.0.0.1:23456/voice/vits?text=text&id=142&format=wav&lang=zh&length=1.4

   The text is "text", the role ID is 142, the audio format is wav, the text language is zh, the speech length is 1.4, and the other parameters are default.

#### check

- GET http://127.0.0.1:23456/voice/check?id=0&model=vits

## POST

- See `api_test.py`

## API KEY

Set `API_KEY_ENABLED = True` in `config.py` to enable API key authentication. The API key is `API_KEY = "api-key"`.
After enabling it, you need to add the `api_key` parameter in GET requests and add the `X-API-KEY` parameter in the header for POST requests.

# Parameter

## VITS

| Name                   | Parameter | Is must | Default          | Type  | Instruction                                                  |
| ---------------------- | --------- | ------- | ---------------- | ----- | ------------------------------------------------------------ |
| Synthesized text       | text      | true    |                  | str   | Text needed for voice synthesis.                             |
| Speaker ID             | id        | false   | From `config.py` | int   | The speaker ID.                                              |
| Audio format           | format    | false   | From `config.py` | str   | Support for wav,ogg,silk,mp3,flac                            |
| Text language          | lang      | false   | From `config.py` | str   | The language of the text to be synthesized. Available options include auto, zh, ja, and mix. When lang=mix, the text should be wrapped in [ZH] or [JA].The default mode is auto, which automatically detects the language of the text |
| Audio length           | length    | false   | From `config.py` | float | Adjusts the length of the synthesized speech, which is equivalent to adjusting the speed of the speech. The larger the value, the slower the speed. |
| Noise                  | noise     | false   | From `config.py` | float | Sample noise, controlling the randomness of the synthesis.   |
| SDP noise              | noisew    | false   | From `config.py` | float | Stochastic Duration Predictor noise, controlling the length of phoneme pronunciation. |
| Segmentation threshold | max       | false   | v                | int   | Divide the text into paragraphs based on punctuation marks, and combine them into one paragraph when the length exceeds max. If max<=0, the text will not be divided into paragraphs. |
| Streaming response     | streaming | false   | false            | bool  | Streamed synthesized speech with faster initial response.    |

## VITS voice conversion

| Name           | Parameter   | Is must | Default | Type | Instruction                                               |
| -------------- | ----------- | ------- | ------- | ---- | --------------------------------------------------------- |
| Uploaded Audio | upload      | true    |         | file | The audio file to be uploaded. It should be in wav or ogg |
| Source Role ID | original_id | true    |         | int  | The ID of the role used to upload the audio file.         |
| Target Role ID | target_id   | true    |         | int  | The ID of the target role to convert the audio to.        |

## HuBert-VITS

| Name              | Parameter | Is must | Default | Type  | Instruction                                                  |
| ----------------- | --------- | ------- | ------- | ----- | ------------------------------------------------------------ |
| Uploaded Audio    | upload    | true    |         | file  | The audio file to be uploaded. It should be in wav or ogg format. |
| Target speaker ID | id        | true    |         | int   | The target  speaker ID.                                      |
| Audio format      | format    | true    |         | str   | wav,ogg,silk                                                 |
| Audio length      | length    | true    |         | float | Adjusts the length of the synthesized speech, which is equivalent to adjusting the speed of the speech. The larger the value, the slower the speed. |
| Noise             | noise     | true    |         | float | Sample noise, controlling the randomness of the synthesis.   |
| sdp noise         | noisew    | true    |         | float | Stochastic Duration Predictor noise, controlling the length of phoneme pronunciation. |

## W2V2-VITS

| Name                   | Parameter | Is must | Default          | Type  | Instruction                                                  |
| ---------------------- | --------- | ------- | ---------------- | ----- | ------------------------------------------------------------ |
| Synthesized text       | text      | true    |                  | str   | Text needed for voice synthesis.                             |
| Speaker ID             | id        | false   | From `config.py` | int   | The speaker ID.                                              |
| Audio format           | format    | false   | From `config.py` | str   | Support for wav,ogg,silk,mp3,flac                            |
| Text language          | lang      | false   | From `config.py` | str   | The language of the text to be synthesized. Available options include auto, zh, ja, and mix. When lang=mix, the text should be wrapped in [ZH] or [JA].The default mode is auto, which automatically detects the language of the text |
| Audio length           | length    | false   | From `config.py` | float | Adjusts the length of the synthesized speech, which is equivalent to adjusting the speed of the speech. The larger the value, the slower the speed. |
| Noise                  | noise     | false   | From `config.py` | float | Sample noise, controlling the randomness of the synthesis.   |
| SDP noise              | noisew    | false   | From `config.py` | float | Stochastic Duration Predictor noise, controlling the length of phoneme pronunciation. |
| Segmentation threshold | max       | false   | From `config.py` | int   | Divide the text into paragraphs based on punctuation marks, and combine them into one paragraph when the length exceeds max. If max<=0, the text will not be divided into paragraphs. |
| Dimensional emotion    | emotion   | false   | 0                | int   | The range depends on the emotion reference file in npy format, such as the  range of the [innnky](https://huggingface.co/spaces/innnky/nene-emotion/tree/main)'s model all_emotions.npy, which is 0-5457. |

## Dimensional emotion

| Name           | Parameter | Is must | Default | Type | Instruction                                                  |
| -------------- | --------- | ------- | ------- | ---- | ------------------------------------------------------------ |
| Uploaded Audio | upload    | true    |         | file | Return the npy file that stores the dimensional emotion vectors. |

## Bert-VITS2

| Name                   | Parameter | Is must | Default          | Type  | Instruction                                                  |
| ---------------------- | --------- | ------- | ---------------- | ----- | ------------------------------------------------------------ |
| Synthesized text       | text      | true    |                  | str   | Text needed for voice synthesis.                             |
| Speaker ID             | id        | false   | From `config.py` | int   | The speaker ID.                                              |
| Audio format           | format    | false   | From `config.py` | str   | Support for wav,ogg,silk,mp3,flac                            |
| Text language          | lang      | false   | From `config.py` | str   | "Auto" is a mode for automatic language detection and is also the default mode. However, it currently only supports detecting the language of an entire text passage and cannot distinguish languages on a per-sentence basis. The other available language options are "zh" and "ja". |
| Audio length           | length    | false   | From `config.py` | float | Adjusts the length of the synthesized speech, which is equivalent to adjusting the speed of the speech. The larger the value, the slower the speed. |
| Noise                  | noise     | false   | From `config.py` | float | Sample noise, controlling the randomness of the synthesis.   |
| SDP noise              | noisew    | false   | From `config.py` | float | Stochastic Duration Predictor noise, controlling the length of phoneme pronunciation. |
| Segmentation threshold | max       | false   | From `config.py` | int   | Divide the text into paragraphs based on punctuation marks, and combine them into one paragraph when the length exceeds max. If max<=0, the text will not be divided into paragraphs. |
| SDP/DP mix ratio       | sdp_ratio | false   | From `config.py` | int   | The theoretical proportion of SDP during synthesis, the higher the ratio, the larger the variance in synthesized voice tone. |

## SSML (Speech Synthesis Markup Language)

Supported Elements and Attributes

`speak` Element

| Attribute | Instruction                                                  | Is must |
| --------- | ------------------------------------------------------------ | ------- |
| id        | Default value is retrieved from `config.py`                  | false   |
| lang      | Default value is retrieved from `config.py`                  | false   |
| length    | Default value is retrieved from `config.py`                  | false   |
| noise     | Default value is retrieved from `config.py`                  | false   |
| noisew    | Default value is retrieved from `config.py`                  | false   |
| max       | Splits text into segments based on punctuation marks. When the sum of segment lengths exceeds `max`, it is treated as one segment. `max<=0` means no segmentation. The default value is 0. | false   |
| model     | Default is `vits`. Options: `w2v2-vits`, `emotion-vits`      | false   |
| emotion   | Only effective when using `w2v2-vits` or `emotion-vits`. The range depends on the npy emotion reference file. | false   |

`voice` Element

Higher priority than `speak`.

| Attribute | Instruction                                                  | Is must |
| --------- | ------------------------------------------------------------ | ------- |
| id        | Default value is retrieved from `config.py`                  | false   |
| lang      | Default value is retrieved from `config.py`                  | false   |
| length    | Default value is retrieved from `config.py`                  | false   |
| noise     | Default value is retrieved from `config.py`                  | false   |
| noisew    | Default value is retrieved from `config.py`                  | false   |
| max       | Splits text into segments based on punctuation marks. When the sum of segment lengths exceeds `max`, it is treated as one segment. `max<=0` means no segmentation. The default value is 0. | false   |
| model     | Default is `vits`. Options: `w2v2-vits`, `emotion-vits`      | false   |
| emotion   | Only effective when using `w2v2-vits` or `emotion-vits`      | false   |

`break` Element

| Attribute | Instruction                                                  | Is must |
| --------- | ------------------------------------------------------------ | ------- |
| strength  | x-weak, weak, medium (default), strong, x-strong             | false   |
| time      | The absolute duration of a pause in seconds (such as `2s`) or milliseconds (such as `500ms`). Valid values range from 0 to 5000 milliseconds. If you set a value greater than the supported maximum, the service will use `5000ms`. If the `time` attribute is set, the `strength` attribute is ignored. | false   |

| Strength | Relative Duration |
| :------- | :---------------- |
| x-weak   | 250 ms            |
| weak     | 500 ms            |
| medium   | 750 ms            |
| strong   | 1000 ms           |
| x-strong | 1250 ms           |

Example

```xml
<speak lang="zh" format="mp3" length="1.2">
    <voice id="92" >这几天心里颇不宁静。</voice>
    <voice id="125">今晚在院子里坐着乘凉，忽然想起日日走过的荷塘，在这满月的光里，总该另有一番样子吧。</voice>
    <voice id="142">月亮渐渐地升高了，墙外马路上孩子们的欢笑，已经听不见了；</voice>
    <voice id="98">妻在屋里拍着闰儿，迷迷糊糊地哼着眠歌。</voice>
    <voice id="120">我悄悄地披了大衫，带上门出去。</voice><break time="2s"/>
    <voice id="121">沿着荷塘，是一条曲折的小煤屑路。</voice>
    <voice id="122">这是一条幽僻的路；白天也少人走，夜晚更加寂寞。</voice>
    <voice id="123">荷塘四面，长着许多树，蓊蓊郁郁的。</voice>
    <voice id="124">路的一旁，是些杨柳，和一些不知道名字的树。</voice>
    <voice id="125">没有月光的晚上，这路上阴森森的，有些怕人。</voice>
    <voice id="126">今晚却很好，虽然月光也还是淡淡的。</voice><break time="2s"/>
    <voice id="127">路上只我一个人，背着手踱着。</voice>
    <voice id="128">这一片天地好像是我的；我也像超出了平常的自己，到了另一个世界里。</voice>
    <voice id="129">我爱热闹，也爱冷静；<break strength="x-weak"/>爱群居，也爱独处。</voice>
    <voice id="130">像今晚上，一个人在这苍茫的月下，什么都可以想，什么都可以不想，便觉是个自由的人。</voice>
    <voice id="131">白天里一定要做的事，一定要说的话，现在都可不理。</voice>
    <voice id="132">这是独处的妙处，我且受用这无边的荷香月色好了。</voice>
</speak>
```

# Communication

Learning and communication,now there is only Chinese [QQ group](https://qm.qq.com/cgi-bin/qm/qr?k=-1GknIe4uXrkmbDKBGKa1aAUteq40qs_&jump_from=webapi&authKey=x5YYt6Dggs1ZqWxvZqvj3fV8VUnxRyXm5S5Kzntc78+Nv3iXOIawplGip9LWuNR/)

# Acknowledgements

- vits:https://github.com/jaywalnut310/vits
- MoeGoe:https://github.com/CjangCjengh/MoeGoe
- emotional-vits:https://github.com/innnky/emotional-vits
- vits-uma-genshin-honkai:https://huggingface.co/spaces/zomehwh/vits-uma-genshin-honkai
- vits_chinese:https://github.com/PlayVoice/vits_chinese
- Bert_VITS2:https://github.com/fishaudio/Bert-VITS2

